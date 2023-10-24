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
    
    keyword = 'Bearer'
    model = User
    
    # run query against database to verify user info by querying user id
    async def authenticate_credentials(self, id):
        
        # query mongo db for user
        try:
            uid = ObjectId(id)
        except:
            raise AuthenticationFailed('Invalid ID')
        user = await collection.find_one({'_id': uid})
        print(user)
        if not user['userActive']:
            raise AuthenticationFailed('User Inactive')
        return (user, None)
        
    # called everytime when accessing restricted router
    def authenticate(self, request):
        print('========================')
        print('|| verify token called ||')
        print('========================')
        # get auth token in request header and concat
        token = request.META.get('HTTP_AUTHORIZATION')
        JWTToken = token[7:]
        print(JWTToken)
        
        if not JWTToken:
            print('no tokens found')
            raise AuthenticationFailed('Token Not Found')

        # decode
        payload = jwt.decode(JWTToken, settings.SECRET_KEY, algorithms='HS256')
        print(payload)
        
        # try:
        
        # except jwt.DecodeError or UnicodeError:
        #     raise AuthenticationFailed('Invalid token')
        # except jwt.ExpiredSignatureError:
        #     raise AuthenticationFailed('Token has expired')
        return self.authenticate_credentials(payload['id'])
