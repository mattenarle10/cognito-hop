import json
import os
import sys

# Add the parent directory to sys.path to allow importing from app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.aws.dynamodb_service import DynamoDBService
from services.repositories.order_repository import OrderRepository
from services.auth.jwt_service import JWTService
from domains.order_domain import OrderDomain
from utils.response_formatter import success_response, error_response

# Initialize services and repositories
dynamodb_service = DynamoDBService()
order_repository = OrderRepository(dynamodb_service)
jwt_service = JWTService()
order_domain = OrderDomain(order_repository, jwt_service)

def handler(event, context):
    """
    HTTP Handler for POST /orders
    Creates a new order for authenticated user
    
    Args:
        event: API Gateway event containing headers and body
        context: Lambda context
        
    Returns:
        API Gateway response with created order details
    """
    try:
        print("Create order request received:", json.dumps(event))
        
        # Extract Authorization header
        headers = event.get('headers') or {}
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        if not auth_header:
            return error_response(
                status_code=401,
                message="Missing Authorization header",
                error_code="MISSING_AUTH_HEADER"
            )
        
        # Extract ID token (remove 'Bearer ' prefix if present)
        id_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
        
        # Extract request body
        body = event.get('body')
        if not body:
            return error_response(
                status_code=400,
                message="Missing request body",
                error_code="MISSING_BODY"
            )
        
        # Parse JSON body
        try:
            order_data = json.loads(body)
        except json.JSONDecodeError:
            return error_response(
                status_code=400,
                message="Invalid JSON in request body",
                error_code="INVALID_JSON"
            )
        
        # Create order using domain layer
        try:
            order_item = order_domain.create_user_order(id_token, order_data)
        except ValueError as e:
            return error_response(
                status_code=400,
                message=str(e),
                error_code="ORDER_CREATION_FAILED"
            )
        
        # Return success response
        return success_response(
            data={
                "order_id": order_item['order_id'],
                "user_id": order_item['user_id'],
                "item_name": order_item['item_name'],
                "quantity": order_item['quantity'],
                "price_per_item": float(order_item['price_per_item']),
                "total_price": float(order_item['total_price']),
                "currency": order_item['currency'],
                "status": order_item['status'],
                "created_at": order_item['created_at']
            },
            message="Order created successfully"
        )
        
    except Exception as e:
        print(f"Error in create order handler: {str(e)}")
        return error_response(
            status_code=500,
            message="Internal server error",
            error_code="INTERNAL_ERROR"
        ) 