import json
import os
import sys

# Add the parent directory to sys.path to allow importing from app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.aws.dynamodb_service import DynamoDBService
from services.repositories.user_repository import UserRepository
from services.repositories.application_repository import ApplicationRepository
from domains.user_domain import UserDomain

# Initialize services and repositories
dynamodb_service = DynamoDBService()
user_repository = UserRepository(dynamodb_service)
application_repository = ApplicationRepository(dynamodb_service)
user_domain = UserDomain(user_repository, application_repository)

def handler(event, context):
    """
    Post-confirmation Lambda trigger for Cognito.
    This function is triggered after a user confirms their registration.
    It saves the user data to DynamoDB and creates an application-user relationship.
    
    Args:
        event: The event from Cognito containing user attributes
        context: Lambda context
        
    Returns:
        The event object to be passed back to Cognito
    """
    try:
        print("Post confirmation trigger received event:", json.dumps(event))
        
        # Extract user attributes from Cognito event
        user_attributes = event['request']['userAttributes']
        
        # Get application context from ClientMetadata
        client_metadata = event['request'].get('clientMetadata', {})
        application_name = client_metadata.get('application_name', '')
        channel_id = client_metadata.get('channel_id', '')
        
        # Use application_name as application_id (or fallback to default for testing)
        application_id = application_name if application_name else "default_app"
        
        print(f"Registration context - Application: {application_name}, Channel: {channel_id}")
        
        # Register the user using the domain layer
        user_id, user_item = user_domain.register_user(user_attributes, application_id)
        
        print(f"Successfully created user {user_id} - will require consent for application {application_id}")
        
        # Return the event to Cognito
        return event
        
    except Exception as e:
        print(f"Error in post confirmation trigger: {str(e)}")
        # In case of error, we still return the event to not block the user confirmation
        return event
