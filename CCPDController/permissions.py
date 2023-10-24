from rest_framework import permissions
from rest_framework.permissions import BasePermission
from CCPDController.utils import get_db_client

# pymongo
db = get_db_client()
collection = db['User']

# QA personal permission
class QAPermission(permissions.BasePermission):
    message = 'Permission Denied'
    
    def has_permission(self, request, view):
        
        # do mongo query to see user role
        return super().has_permission(request, view)

        
# determine if user have permission to access inventory object
class IsInventoryOwnerPermission(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            # always allow GET HEAD OPTION method
            if request.method in permissions.SAFE_METHODS:
                return True
            
            # query db see if object owned by user
            return obj.owner == request.user
  
# admin permission   
class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # query database to see if user is admin
        return super().has_permission(request, view)
    

# user blocked by IP
class BlockedPermission(permissions.BasePermission):
    message = 'You Are Blocked From Our Service'
    
    def has_permission(self, request, view):
        ipAddress = request.META['REMOTE_ADDR']
        # query database for blocked ip address
        # blocked = 
