import os
import boto3
from decimal import Decimal

class DynamoDBService:
    """
    service for dynamodb operations in client backend
    handles both orders table and main table access
    """
    
    def __init__(self):
        """initialize dynamodb service with table names from environment"""
        self.dynamodb = boto3.resource('dynamodb')
        self.orders_table_name = os.environ.get('ORDERS_TABLE', 'matt-cognito-hop-orders')
        self.main_table_name = os.environ.get('MAIN_TABLE', 'matt-cognito-hop-main')
        self.orders_table = self.dynamodb.Table(self.orders_table_name)
        self.main_table = self.dynamodb.Table(self.main_table_name)
    
    def query_orders_by_user(self, user_id):
        """
        query orders table for a specific user
        
        args:
            user_id (str): the user id (like user-9fef7f58)
            
        returns:
            list: list of order items for the user
        """
        try:
            response = self.orders_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('PK').eq(user_id)
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"error querying orders for user {user_id}: {str(e)}")
            return []
    
    def put_order(self, order_item):
        """
        create a new order in orders table
        
        args:
            order_item (dict): order data with all required fields
            
        returns:
            bool: true if successful, false otherwise
        """
        try:
            # convert price fields to decimal for dynamodb
            if 'price_per_item' in order_item:
                order_item['price_per_item'] = Decimal(str(order_item['price_per_item']))
            if 'total_price' in order_item:
                order_item['total_price'] = Decimal(str(order_item['total_price']))
            
            # save to orders table
            self.orders_table.put_item(Item=order_item)
            print(f"successfully created order {order_item.get('order_id')}")
            return True
            
        except Exception as e:
            print(f"error creating order: {str(e)}")
            return False

    def scan_users_by_sub(self, cognito_sub):
        """
        find user by cognito sub in main table
        note: in production, use gsi. for now, scan is ok with minimal data
        
        args:
            cognito_sub (str): cognito user sub
            
        returns:
            dict: user item if found, none otherwise
        """
        try:
            response = self.main_table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('user') & 
                               boto3.dynamodb.conditions.Attr('sub').eq(cognito_sub)
            )
            
            items = response.get('Items', [])
            return items[0] if items else None
            
        except Exception as e:
            print(f"error finding user by sub {cognito_sub}: {str(e)}")
            return None 