from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path("getInventoryBySku", views.getInventoryBySku, name="getInventoryBySku"),
    path("createInventory", views.createInventory, name="createInventory"),
    path("deleteInventoryBySku", views.deleteInventoryBySku, name="deleteInventoryBySku"), 
    path("updateInventoryBySku", views.updateInventoryBySku, name="updateInventoryBySku"),
    path("getInventoryByOwnerId", views.getInventoryByOwnerId, name="getInventoryByOwnerId")
]
