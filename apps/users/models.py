from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    username  = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username
    
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.jpg')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return self.user.username
    