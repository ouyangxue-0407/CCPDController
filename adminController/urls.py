from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path('checkAdminToken', views.checkAdminToken, name='checkAdminToken'),
    path('adminLogin', views.adminLogin, name='adminLogin'),
    path('deleteUserById', views.deleteUserById, name="deleteUserById"),
    path('setUserActive', views.setUserActive, name="setUserActive"),
    path('updatePasswordById', views.updatePasswordById, name="updatePasswordById"),
    path('getAllInventory', views.getAllInventory, name="getAllInventory")
]
