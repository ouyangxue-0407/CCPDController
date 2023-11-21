from django.db import models

class InvitationCode(models.Model): 
    code: models.CharField(max_length=100)
    available: models.BooleanField(max_length=5)
    exp: models.CharField(max_length=25)
    
    # constructor input all info
    def __init__(self, code, available, exp) -> None:
        self.code = code
        self.available = available
        self.exp = exp
        
    # return inventory sku
    def __str__(self) -> str:
        return str(self.code)