import jwt
from rest_framework.authentication import get_authorization_header, TokenAuthentication
from bson.objectid import ObjectId
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from CCPDController.utils import get_db_client
from userController.models import User

# pymongo
db = get_db_client()
collection = db['User']

# customized authentication class used in settings
class JWTAuthentication(TokenAuthentication):
    # run query against database to verify user info by querying user id
    def authenticate_credentials(self, id):
        # if id cannot convert into ObjectId, throw error
        try:
            uid = ObjectId(id)
        except:
            raise AuthenticationFailed('Invalid ID')
        
        # get only id status and role
        user = collection.find_one({'_id': uid}, {'userActive': 1, 'role': 1})
        
        # check user activation status
        if not user['userActive']:
            raise AuthenticationFailed('User Inactive')
        
        # return type have to be tuple
        return (user, user['role'])
        
    # called everytime when accessing restricted router
    def authenticate(self, request):
        try:
            # get auth token in request header and concat
            token = request.META.get('HTTP_AUTHORIZATION')
            
            # remove space and auth type
            JWTToken = token[7:]
            
            # if no token throw not found
            if not JWTToken or len(JWTToken) < 1:
                raise AuthenticationFailed('Token Not Found')

            # decode jwt and retrive user id
            payload = jwt.decode(JWTToken, settings.SECRET_KEY, algorithms='HS256')
        except jwt.DecodeError or UnicodeError:
            raise AuthenticationFailed('Invalid token')
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        return self.authenticate_credentials(payload['id'])
