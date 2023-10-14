from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path("getUserNameById", views.getUserNameById, name="getUserNameById"),
    path("getIfEmailExist", views.getIfEmailExist, name="getIfEmailExist"),
    path("validateUser", views.validateUser, name="validateUser"),
    path("registerUser", views.registerUser, name="registerUser"),
    path("deleteUserById", views.deleteUserById, name="deleteUserById"),
    path("changePasswordById", views.deleteUserById, name="changePasswordById")
]
