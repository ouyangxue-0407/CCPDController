from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path("downloadImage", views.downloadSingleImage, name="downloadSingleImage"),
    path("bulkDownloadImages", views.bulkDownloadImages, name="bulkDownloadImages"), 
    path("uploadSingleImage", views.uploadSingleImage, name="uploadSingleImage"),
    path("bulkUploadImages", views.bulkUploadImages, name="bulkUploadImage"),
    path("listBlobContainers", views.listBlobContainers, name="listBlobContainers")
]
