class OrderDomain:
    """
    domain for order-related business logic
    handles jwt validation and order operations
    """
    
    def __init__(self, order_repository, jwt_service):
        """
        initialize order domain
        
        args:
            order_repository: instance of OrderRepository
            jwt_service: instance of JWTService
        """
        self.order_repository = order_repository
        self.jwt_service = jwt_service
    
    def get_user_orders(self, id_token):
        """
        get orders for user by validating their jwt token
        
        args:
            id_token (str): cognito id token from authorization header
            
        returns:
            list: list of user's orders
            
        raises:
            ValueError: if token invalid or user not found
        """
        # validate jwt and extract user info
        try:
            user_info = self.jwt_service.extract_user_info(id_token)
            cognito_sub = user_info['sub']
        except ValueError as e:
            raise ValueError(f"invalid token: {str(e)}")
        
        # find user by cognito sub
        user = self.order_repository.find_user_by_cognito_sub(cognito_sub)
        if not user:
            raise ValueError("user not found in system")
        
        user_id = user['PK']  # extract user_id
        
        # get orders for this user
        orders = self.order_repository.get_orders_by_user_id(user_id)
        
        return orders
    
    def create_user_order(self, id_token, order_data):
        """
        create a new order for user after validating their jwt token
        
        args:
            id_token (str): cognito id token from authorization header
            order_data (dict): order information (item_name, quantity, price_per_item)
            
        returns:
            dict: created order item
            
        raises:
            ValueError: if token invalid, user not found, or validation fails
        """
        # validate jwt and extract user info
        try:
            user_info = self.jwt_service.extract_user_info(id_token)
            cognito_sub = user_info['sub']
        except ValueError as e:
            raise ValueError(f"invalid token: {str(e)}")
        
        # find user by cognito sub
        user = self.order_repository.find_user_by_cognito_sub(cognito_sub)
        if not user:
            raise ValueError("user not found in system")
        
        user_id = user['PK']  # extract user_id
        
        # validate order data
        self._validate_order_data(order_data)
        
        # create order
        order_item = self.order_repository.create_order(user_id, order_data)
        if not order_item:
            raise ValueError("failed to create order")
        
        return order_item
    
    def _validate_order_data(self, order_data):
        """
        validate order data before creation
        
        args:
            order_data (dict): order information to validate
            
        raises:
            ValueError: if validation fails
        """
        required_fields = ['item_name', 'quantity', 'price_per_item']
        
        # check required fields
        for field in required_fields:
            if field not in order_data:
                raise ValueError(f"missing required field: {field}")
        
        # validate item name
        if not order_data['item_name'].strip():
            raise ValueError("item_name cannot be empty")
        
        # validate quantity
        if not isinstance(order_data['quantity'], int) or order_data['quantity'] <= 0:
            raise ValueError("quantity must be a positive integer")
        
        # validate price
        if not isinstance(order_data['price_per_item'], (int, float)) or order_data['price_per_item'] <= 0:
            raise ValueError("price_per_item must be a positive number") 