import json

def format_response(status_code, body):
    """
    format a standard api gateway response
    
    args:
        status_code (int): http status code
        body (dict): response body
        
    returns:
        dict: formatted response for api gateway
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        },
        'body': json.dumps(body)
    }

def success_response(data=None, message=None):
    """
    format a successful response
    
    args:
        data (dict, optional): response data
        message (str, optional): success message
        
    returns:
        dict: formatted success response
    """
    body = {
        'success': True
    }
    
    if data is not None:
        body['data'] = data
        
    if message is not None:
        body['message'] = message
        
    return format_response(200, body)

def error_response(status_code, message, error_code=None):
    """
    format an error response
    
    args:
        status_code (int): http status code
        message (str): error message
        error_code (str, optional): error code
        
    returns:
        dict: formatted error response
    """
    body = {
        'success': False,
        'message': message
    }
    
    if error_code is not None:
        body['error_code'] = error_code
        
    return format_response(status_code, body) 