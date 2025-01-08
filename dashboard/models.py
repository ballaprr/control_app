from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Arena(AbstractUser):
    brightness = models.IntegerField(default=75)

    def __str__(self):
        return self.username
    

class Device(models.Model):
    name = models.CharField(max_length=255)
    device_id = models.IntegerField(unique=True)
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name='devices')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (ID:- {self.device_id})"
    
    