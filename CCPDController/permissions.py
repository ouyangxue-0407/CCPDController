from rest_framework import permissions
from rest_framework.permissions import BasePermission
from CCPDController.utils import get_db_client

# pymongo
db = get_db_client()
collection = db['User']

# user object will be pass into here from authentication 
# auth = ROLE
# user = {
#   '_id': ObjectId(xxx),
#   'userActive': xxx,
#   'role': xxx
# }

# QA personal permission
class IsQAPermission(permissions.BasePermission):
    message = 'Permission Denied, QAPersonal Only!'
    def has_permission(self, request, view):
        # mongo db query
        # grant if user is qa personal and user is active
        if request.auth == 'QAPersonal' and request.user['userActive'] == True:
            return True

# admin permission
class IsAdminPermission(permissions.BasePermission):
    message = 'Permission Denied, Admin Only!'
    def has_permission(self, request, view):
        if request.auth == 'Admin' and bool(request.user['userActive']) == True :
            return True

# user blocked by IP black list
class BlockedPermission(permissions.BasePermission):
    message = 'You Are Blocked From Our Service'
    
    def has_permission(self, request, view):
        ipAddress = request.META['REMOTE_ADDR']
        # query database for blocked ip address
        # blocked = 
