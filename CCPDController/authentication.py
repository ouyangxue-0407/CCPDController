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
    def authenticate(self, request):
        print('========================')
        print('|| verify token called ||')
        print('========================')
        
        # get auth token in request header
        token = request.META.get('HTTP_AUTHORIZATION')
        JWTToken = token[7:]
        
        print(JWTToken)
        
        if not JWTToken:
            print('no tokens found')
            return None 


        print('========================')
        print('|| decode token called ||')
        print('========================')
        
        # decode
        payload = jwt.decode(JWTToken, settings.SECRET_KEY, algorithms='HS256')
        print(payload)
        
        
        uid = ObjectId(payload['id'])
        print(uid)
        
        # query mongo db for user
        user = collection.find_one({'_id': uid})
        
        print(user)

        # try:

        
        # except jwt.DecodeError or UnicodeError:
        #     raise AuthenticationFailed('Invalid token')
        # except jwt.ExpiredSignatureError:
        #     raise AuthenticationFailed('Token has expired')
        
        # if not activate throw error
        if not user['userActive']:
            raise AuthenticationFailed('User inactive')
        return True
