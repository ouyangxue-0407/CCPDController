from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path("getUserById", views.getUserById, name="getUserById"),
    path("validateUser", views.validateUser, name="validateUser"),
    path("registerUser", views.registerUser, name="registerUser"),
    path("deleteUserById", views.deleteUserById, name="deleteUserById"),
    path("updatePasswordById", views.updatePasswordById, name="updatePasswordById")
]
