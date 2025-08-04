import uuid
from datetime import datetime

class OrderRepository:
    """
    repository for order data access operations
    handles querying and creating orders
    """
    
    def __init__(self, dynamodb_service):
        """initialize with dynamodb service"""
        self.dynamodb_service = dynamodb_service
    
    def get_orders_by_user_id(self, user_id):
        """
        get all orders for a specific user
        
        args:
            user_id (str): the user id (like user-9fef7f58)
            
        returns:
            list: list of order items for the user
        """
        return self.dynamodb_service.query_orders_by_user(user_id)
    
    def create_order(self, user_id, order_data):
        """
        create a new order for a user
        
        args:
            user_id (str): the user id
            order_data (dict): order information (item_name, quantity, price_per_item)
            
        returns:
            dict: created order item if successful, none otherwise
        """
        # generate unique order id
        order_id = f"order-{str(uuid.uuid4())[:8]}"
        
        # calculate total price
        total_price = order_data['quantity'] * order_data['price_per_item']
        
        # create order item following jambyref schema + minimal business fields
        order_item = {
            "PK": user_id,
            "SK": order_id,
            "user_id": user_id,
            "order_id": order_id,
            "item_name": order_data['item_name'],
            "quantity": order_data['quantity'],
            "price_per_item": order_data['price_per_item'],
            "total_price": total_price,
            "currency": "PHP",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # save to dynamodb
        success = self.dynamodb_service.put_order(order_item)
        
        if success:
            return order_item
        else:
            return None
    
    def find_user_by_cognito_sub(self, cognito_sub):
        """
        find user record by cognito sub
        
        args:
            cognito_sub (str): cognito user sub
            
        returns:
            dict: user item if found, none otherwise
        """
        return self.dynamodb_service.scan_users_by_sub(cognito_sub) 