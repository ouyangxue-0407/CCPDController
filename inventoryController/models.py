from django.db import models
import os
from typing import Any
from jsonfield import JSONField

class InventoryItem(models.Model): 
    _id: models.AutoField(primary_key=True)
    time: models.CharField(max_length=30)
    sku: models.CharField(max_length=10)
    condition: models.CharField(max_length=10)
    description: models.TextField()
    owner: models.CharField(max_length=32)
    images: JSONField()
    
    # constructor input all info
    def __init__(self, time, sku, condition, description, owner, images) -> None:
        self.time = time
        self.sku = sku
        self.condition=condition
        self.description = description
        self.owner = owner
        self.images = images
        
    # return inventory sku
    def __str__(self) -> str:
        return str(self.sku)