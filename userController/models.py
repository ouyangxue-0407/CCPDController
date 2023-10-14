from django.db import models

class User(models.Model): 
    _id: models.AutoField(primary_key=True)
    name: models.CharField(max_length=20)
    email: models.EmailField(max_length=40)
    password: models.CharField(max_length=45) # store hashed string only
    role: models.CharField(max_length=10)
    registrationDate: models.CharField(max_length=30)
    userActive: models.BooleanField()
    
    # constructor input all info
    def __init__(self, name, email, password, role, registrationDate, userActive ) -> None:
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.registrationDate = registrationDate
        self.userActive = userActive
        
    # return inventory sku
    def __str__(self) -> str:
        return str(self.email)