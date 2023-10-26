from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path('login', views.login, name="login"),
    path("registerUser", views.registerUser, name="registerUser"),
    path("getUserById", views.getUserById, name="getUserById"),
    path("updatePasswordById", views.updatePasswordById, name="updatePasswordById")
]
