from django.db import models
import os
# import time
from typing import Any

# Create your models here.
class InventoryItem(models.Model): 
    _id: models.AutoField(primary_key=True)
    time: models.TimeField()
    sku: models.CharField(max_length=10)
    description: models.TextField()
    owner: models.CharField(max_length=32)
    # images: models.field
    
    def __init__(time, sku, description, owner) -> None:
        time = time
        sku = sku
        description = description
        owner = owner
        
    # return inventory sku
    def __str__(self) -> str:
        return self.sku