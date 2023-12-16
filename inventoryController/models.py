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
        ('Amazon', 'Amazon'),
        ('eBay', 'eBay'),
        ('Official Website', 'Official Website'),
        ('Other', 'Other')
    ]
    
    MARKETPLACE_CHOISES = [
        ('Hibid', 'Hibid'),
        ('Retail', 'Retail'),
        ('eBay', 'eBay'),
        ('Wholesale', 'Wholesale'),
        ('Other', 'Other')
    ]
    
    _id: models.AutoField(primary_key=True)
    time: models.CharField(max_length=30)
    sku: models.IntegerField(max_length=10)
    itemCondition: models.CharField(max_length=14, choices=CONDITION_CHOISES)
    comment: models.TextField(max_length=100)
    link: models.TextField(max_length=300)
    platform: models.CharField(max_length=17, choices=PLATFORM_CHOISES)
    shelfLocation: models.CharField(max_length=4)
    amount: models.IntegerField(max_length=3)
    owner: models.CharField(max_length=32)
    ownerName: models.CharField(max_length=40)
    marketplace: models.CharField(max_length=10, choices=MARKETPLACE_CHOISES)
    
    # constructor input all info
    def __init__(self, time, sku, itemCondition, comment, link, platform, shelfLocation, amount, owner, ownerName, marketplace) -> None:
        self.time = time
        self.sku = sku
        self.itemCondition=itemCondition
        self.comment = comment
        self.link = link
        self.platform = platform
        self.shelfLocation = shelfLocation
        self.amount = amount
        self.owner = owner
        self.ownerName = ownerName
        self.marketplace = marketplace
        
    # return inventory sku
    def __str__(self) -> str:
        return str(self.sku)