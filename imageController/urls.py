from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path("uploadImage/<str:sku>", views.uploadImage, name="uploadImage"),
    path("downloadAllImagesBySKU", views.downloadAllImagesBySKU, name="downloadAllImagesBySKU"),
    path("listBlobContainers", views.listBlobContainers, name="listBlobContainers")
]
