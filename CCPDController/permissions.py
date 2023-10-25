from rest_framework import permissions
from rest_framework.permissions import BasePermission
from CCPDController.utils import get_db_client

# pymongo
db = get_db_client()
collection = db['User']

# QA personal permission
class IsQAPermission(permissions.BasePermission):
    message = 'Permission Denied, QAPersonal Only'
    def has_permission(self, request, view):        
        print(" HAS PERMISSION :: ")
        print(request.user)
        print(request.auth)
        
        # mongo db query
        # grant if user is qa personal and user is active
        if request.auth == 'QAPersonal' and request.user['userActive'] == True:
            return True

# determine if user have permission to access inventory object
class IsInventoryOwnerPermission(permissions.BasePermission):
    message = 'Permission Denied, Only Owner Have Access'
    def has_object_permission(self, request, view, obj):
        # always allow GET HEAD OPTION method
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # query db see if object owned by user
        return obj.owner == request.user

# admin permission
class IsAdminPermission(permissions.BasePermission):
    message = 'Permission Denied, Admin Only!'
    
    def has_permission(self, request, view):
        # query database to see if user is admin
        return super().has_permission(request, view)

# user blocked by IP black list
class BlockedPermission(permissions.BasePermission):
    message = 'You Are Blocked From Our Service'
    
    def has_permission(self, request, view):
        ipAddress = request.META['REMOTE_ADDR']
        # query database for blocked ip address
        # blocked = 
