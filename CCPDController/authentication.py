import jwt
from rest_framework.authentication import get_authorization_header, TokenAuthentication
from bson.objectid import ObjectId
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from CCPDController.utils import get_db_client

# pymongo
db = get_db_client()
collection = db['User']

# customized authentication class used in settings
class JWTAuthentication(TokenAuthentication): 
    def verifyToken(self, token):
        try:
            # decode
            payload = jwt.decode(token, settings.SECRET_KEY)
            uid = ObjectId(payload['id'])

            print(token)
            
            # query mongo db for user
            user = collection.find_one({'_id': uid})

        # expect errors
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token')
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        
        # if not activate throw error
        if not user['userActive']:
            raise AuthenticationFailed('User inactive or deleted')
        return payload
