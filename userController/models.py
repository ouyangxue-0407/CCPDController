from django.db import models
from django.core.validators import MinLengthValidator

class User(models.Model): 
    _id: models.AutoField(primary_key=True)
    name: models.CharField(max_length=20, validators=[MinLengthValidator(3, 'Need to input a longer name')])
    email: models.EmailField(max_length=45, validators=[MinLengthValidator(8, 'Email Invalid')])
    password: models.CharField(max_length=45, validators=[MinLengthValidator(8, 'password Invalid')])
    role: models.CharField(max_length=15, validators=[MinLengthValidator(8, 'role Invalid')])
    registrationDate: models.CharField(max_length=30, validators=[MinLengthValidator(8,'Registration date invalid')])
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