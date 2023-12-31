from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path("uploadImage/<str:owner>/<str:sku>", views.uploadImage, name="uploadImage"),
    path("downloadAllImagesBySKU", views.downloadAllImagesBySKU, name="downloadAllImagesBySKU"),
    path("getUrlsBySku", views.getUrlsBySku, name="getUrlsBySku"),
    
]
