from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path("getInventoryBySku", views.getInventoryBySku, name="getInventoryBySku"),
    path("createInventory", views.createInventory, name="createInventory"),
    path("deleteInventoryBySku", views.deleteInventoryBySku, name="deleteInventoryBySku"), 
    path("updateInventoryBySku/<str:sku>", views.updateInventoryBySku, name="updateInventoryBySku"),
    path("getInventoryByOwnerId/<int:page>", views.getInventoryByOwnerId, name="getInventoryByOwnerId"),
    path("getInventoryInfoByOwnerId", views.getInventoryInfoByOwnerId, name="getInventoryInfoByOwnerId"),
    path("getAllShelfLocations", views.getAllShelfLocations, name="getAllShelfLocations"),
    path("getInstockByPage", views.getInstockByPage, name="getInstockByPage"),
    path("generateDescriptionBySku", views.generateDescriptionBySku, name="generateDescriptionBySku"),
    path("scrapeInfoBySkuAmazon", views.scrapeInfoBySkuAmazon, name="scrapeInfoBySkuAmazon"),
    path("scrapePriceBySkuHomeDepot", views.scrapePriceBySkuHomeDepot, name="scrapePriceBySkuHomeDepot"),
    path("sendInstockCSV", views.sendInstockCSV, name="sendInstockCSV"),
    path("sendQACSV", views.sendQACSV, name="sendQACSV"),
]
