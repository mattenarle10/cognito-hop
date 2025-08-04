import os
import json
import urllib.request
from jose import jwt, JWTError

class JWTService:
    """
    service for validating cognito tokens using public keys
    think of this as: "is this jwt really from cognito?"
    """
    
    def __init__(self):
        """grab cognito variables from environment variables"""
        self.user_pool_id = os.environ.get('COGNITO_USER_POOL_ID')
        self.app_client_id = os.environ.get('COGNITO_APP_CLIENT_ID')
        self.region = os.environ.get('AWS_REGION', 'ap-southeast-2')
        
        # this is cognito's "phone book" of public keys
        self.jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        self.jwks = None  # cache the keys so we don't download every time
    
    def _get_jwks(self):
        """download the public keys from cognito (only once, then cache)"""
        if self.jwks is None:
            print(f"downloading public keys from: {self.jwks_url}")
            # step 1: ask cognito for their public key directory
            with urllib.request.urlopen(self.jwks_url) as response:
                self.jwks = json.loads(response.read().decode('utf-8'))
        return self.jwks
    
    def _get_key_for_token(self, token_header):
        """find which key cognito used to sign this specific token"""
        jwks = self._get_jwks()
        
        # step 2: look through all keys to find the one with matching kid
        for key in jwks['keys']:
            if key['kid'] == token_header['kid']:  # found it!
                return key
        
        # step 3: if we get here, something's wrong
        raise ValueError("can't find the key for this token - might be fake?")
    
    def validate_id_token(self, id_token):
        """
        main function: verify if this jwt is real and extract user info
        this is like checking if a check is real using the bank's signature
        """
        try:
            print("checking if this jwt token is legit...")
            
            # step 1: peek at jwt header to see which key was used
            token_header = jwt.get_unverified_header(id_token)
            
            # step 2: get the matching public key from cognito
            key = self._get_key_for_token(token_header)
            
            # step 3: verify the signature using rsa + sha256 magic
            decoded_token = jwt.decode(
                id_token,
                key,
                algorithms=['RS256'],  # only allow rs256
                audience=self.app_client_id,  # make sure token is for our app
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"  # from our cognito
            )
            
            print(f"token is valid! user: {decoded_token.get('sub')}")
            return decoded_token
            
        except JWTError as e:
            print(f"jwt verification failed: {str(e)}")
            raise ValueError(f"bad token: {str(e)}")
        except Exception as e:
            print(f"something went wrong: {str(e)}")
            raise ValueError(f"token check failed: {str(e)}")
    
    def extract_user_info(self, id_token):
        """
        convenient function: verify token + extract user details
        this is what we call from our api handlers
        """
        # first verify the token is real (all the crypto happens here)
        decoded_token = self.validate_id_token(id_token)
        
        # then extract the useful user info from the verified payload
        return {
            'sub': decoded_token.get('sub'),  # cognito user id (never changes)
            'email': decoded_token.get('email'),  # user's email
            'name': decoded_token.get('name'),  # user's display name
            'email_verified': decoded_token.get('email_verified'),  # is email confirmed?
            'token_use': decoded_token.get('token_use'),  # should be "id"
            'cognito:user_status': decoded_token.get('cognito:user_status')  # account status
        } 