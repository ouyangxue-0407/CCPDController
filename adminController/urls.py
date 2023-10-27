from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path('deleteUserById', views.deleteUserById, name="deleteUserById"),
    path('setUserActive', views.setUserActive, name="setUserActive"),
    path('updatePasswordById', views.updatePasswordById, name="updatePasswordById"),
]
