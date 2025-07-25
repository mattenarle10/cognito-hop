import re
from datetime import datetime

class UserProfileDomain:
    """
    Domain class for user profile-related business logic.
    Handles profile updates with validation and coordination between services.
    """
    
    def __init__(self, cognito_user_service, user_repository):
        """
        Initialize the UserProfileDomain with services.
        
        Args:
            cognito_user_service: Instance of CognitoUserService
            user_repository: Instance of UserRepository
        """
        self.cognito_user_service = cognito_user_service
        self.user_repository = user_repository
    
    def update_user_profile(self, access_token, user_id, updates):
        """
        Update user profile with validation and business logic.
        
        Args:
            access_token (str): User's Cognito access token
            user_id (str): User ID from DynamoDB
            updates (dict): Dictionary of attributes to update
            
        Returns:
            dict: Result with success status and updated fields
            
        Raises:
            ValueError: If validation fails or update is not allowed
        """
        # Validate the updates
        validated_updates = self._validate_updates(updates)
        
        # Update in Cognito
        success = self.cognito_user_service.update_user_attributes(access_token, validated_updates)
        
        if not success:
            raise ValueError("Failed to update profile in Cognito")
        
        # Optional: Sync back to DynamoDB for consistency
        # This could be useful for queries that don't require Cognito token
        if validated_updates and user_id:
            self._sync_to_dynamodb(user_id, validated_updates)
        
        return {
            "success": True,
            "updated_fields": list(validated_updates.keys()),
            "message": "Profile updated successfully"
        }
    
    def _validate_updates(self, updates):
        """
        Validate profile update fields and values.
        
        Args:
            updates (dict): Raw updates from request
            
        Returns:
            dict: Validated and cleaned updates
            
        Raises:
            ValueError: If validation fails
        """
        if not updates or not isinstance(updates, dict):
            raise ValueError("Updates must be a non-empty dictionary")
        
        # Define allowed fields and their validation rules
        allowed_fields = {
            'name': self._validate_name,
            'phone_number': self._validate_phone_number,
            'gender': self._validate_gender,
            'custom:gender': self._validate_gender,  # Allow custom:gender attribute
            'custom:accepts_marketing': self._validate_boolean_string
        }
        
        validated_updates = {}
        
        for field, value in updates.items():
            if field not in allowed_fields:
                raise ValueError(f"Field '{field}' is not allowed for update")
            
            # Validate the specific field
            cleaned_value = allowed_fields[field](value)
            validated_updates[field] = cleaned_value
        
        return validated_updates
    
    def _validate_name(self, name):
        """Validate user name field"""
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        
        name = name.strip()
        
        if len(name) < 1:
            raise ValueError("Name cannot be empty")
        
        if len(name) > 100:
            raise ValueError("Name cannot exceed 100 characters")
        
        # Check for basic name format (letters, spaces, common punctuation)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
            raise ValueError("Name contains invalid characters")
        
        return name
    
    def _validate_phone_number(self, phone):
        """Validate phone number field"""
        if not phone or not isinstance(phone, str):
            raise ValueError("Phone number must be a non-empty string")
        
        phone = phone.strip()
        
        # Basic phone validation - adjust based on your requirements
        if not re.match(r"^\+?[\d\s\-\(\)]{10,15}$", phone):
            raise ValueError("Invalid phone number format")
        
        return phone
    
    def _validate_gender(self, gender):
        """Validate gender field"""
        if not gender or not isinstance(gender, str):
            raise ValueError("Gender must be a non-empty string")
        
        gender = gender.strip().lower()
        
        # Define allowed gender values
        allowed_genders = {'male', 'female', 'other', 'prefer not to say'}
        
        if gender not in allowed_genders:
            raise ValueError(f"Gender must be one of: {', '.join(allowed_genders)}")
        
        return gender
    
    def _validate_boolean_string(self, value):
        """Validate boolean string field (for custom attributes)"""
        if not isinstance(value, str):
            raise ValueError("Boolean string must be a string value")
            
        value = value.strip().lower()
        
        if value not in ['true', 'false']:
            raise ValueError("Boolean string must be 'true' or 'false'")
            
        return value
    
    def _sync_to_dynamodb(self, user_id, updates):
        """
        Optionally sync updated profile data back to DynamoDB.
        This ensures consistency between Cognito and DynamoDB.
        
        Args:
            user_id (str): User ID
            updates (dict): Validated updates
        """
        try:
            # Get current user record
            user = self.user_repository.get_user_by_id(user_id)
            
            if user:
                # Update the user record with new values
                update_expression = "SET "
                expression_attribute_values = {}
                expression_attribute_names = {}
                expression_parts = []
                
                # Reserved keywords that need attribute names
                reserved_keywords = {'name', 'status', 'type', 'data', 'timestamp', 'count', 'key'}
                
                for field, value in updates.items():
                    # Sanitize field name for use in expression attribute values (remove colons)
                    sanitized_field = field.replace(':', '_')
                    
                    if field.lower() in reserved_keywords or ':' in field:
                        # Use expression attribute names for reserved keywords or fields with colons
                        attr_name = f"#{sanitized_field}"
                        expression_parts.append(f"{attr_name} = :{sanitized_field}")
                        expression_attribute_names[attr_name] = field
                    else:
                        expression_parts.append(f"{field} = :{sanitized_field}")
                    
                    expression_attribute_values[f":{sanitized_field}"] = value
                
                # Add updated timestamp (also a reserved keyword)
                expression_parts.append("#updated_at = :updated_at")
                expression_attribute_names["#updated_at"] = "updated_at"
                expression_attribute_values[":updated_at"] = datetime.now().isoformat()
                
                update_expression += ", ".join(expression_parts)
                
                # Update in DynamoDB
                self.user_repository.dynamodb_service.update_item(
                    key={"PK": user_id, "SK": "user"},
                    update_expression=update_expression,
                    expression_attribute_values=expression_attribute_values,
                    expression_attribute_names=expression_attribute_names
                )
                
                print(f"Successfully synced profile updates to DynamoDB for user {user_id}")
            
        except Exception as e:
            print(f"Warning: Failed to sync profile updates to DynamoDB: {str(e)}")
            # Don't fail the whole operation if DynamoDB sync fails
            pass 