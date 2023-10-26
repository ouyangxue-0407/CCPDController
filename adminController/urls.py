from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path('login', views.login, name="login"),
]
