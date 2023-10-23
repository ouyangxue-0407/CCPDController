from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ["email", "password"]
        
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["name", "roll", "city"]
