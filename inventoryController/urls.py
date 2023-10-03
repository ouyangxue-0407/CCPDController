from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path("createInventory", views.createInventory, name="createInventory"),
    path("deleteInventory", views.deleteInventory, name="deleteInventory"), 
    path("updateInventory", views.updateInventory, name="updateInventory"),
    path("getInventoryBySku", views.getInventoryBySku, name="getInventoryBySku"),
    path("getInventoryByOwner", views.getInventoryByOwner, name="getInventoryByOwner")
]
