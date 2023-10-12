from django.db import models
import os
from typing import Any
from jsonfield import JSONField

class InventoryItem(models.Model): 
    _id: models.AutoField(primary_key=True)
    time: models.CharField(max_length=30)
    sku: models.CharField(max_length=10)
    itemCondition: models.CharField(max_length=10)
    comment: models.TextField()
    link: models.TextField()
    platform: models.CharField(max_length=10)
    shelfLocation: models.CharField(max_length=4)
    amount: models.IntegerField(max_length=3)
    owner: models.CharField(max_length=32)
    # images: JSONField()
    
    # constructor input all info
    def __init__(self, time, sku, itemCondition, comment, link, platform, shelfLocation, amount, owner) -> None:
        self.time = time
        self.sku = sku
        self.itemCondition=itemCondition
        self.comment = comment
        self.link = link
        self.platform = platform
        self.shelfLocation = shelfLocation
        self.amount = amount
        self.owner = owner
        # self.images = images
        
    # return inventory sku
    def __str__(self) -> str:
        return str(self.sku)