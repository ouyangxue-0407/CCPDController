from django.db import models
import os
from typing import Any
from jsonfield import JSONField

class InventoryItem(models.Model): 
    CONDITION_CHOISES = [
        ('New', 'New'),
        ('Sealed', 'Sealed'),
        ('Used', 'Used'),
        ('Used Like New', 'Used Like New'),
        ('Damaged', 'Damaged'),
        ('As Is', 'As Is'),
    ]
    
    PLATFORM_CHOISES = [
        ('Amazon', 'AMAZON'),
        ('eBay', 'eBay'),
        ('Official Website', 'Official Website'),
        ('Other', 'Other')
    ]
    
    _id: models.AutoField(primary_key=True)
    time: models.CharField(max_length=30)
    sku: models.IntegerField(max_length=10)
    itemCondition: models.CharField(max_length=14, choices=CONDITION_CHOISES)
    comment: models.TextField()
    link: models.TextField()
    platform: models.CharField(max_length=16, choices=PLATFORM_CHOISES)
    shelfLocation: models.CharField(max_length=4)
    amount: models.IntegerField(max_length=3)
    owner: models.CharField(max_length=32)
    
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
        
    # return inventory sku
    def __str__(self) -> str:
        return str(self.sku)