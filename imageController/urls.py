from django.urls import path
from . import views

# 
urlpatterns = [
    path("single", views.singleImage, name="singleImage"),
    path("bulk", views.bulkImage, name="bulkImage")
]
