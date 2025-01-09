from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Arena(AbstractUser):
    username = None
    email = None
    arena_name = models.CharField(max_length=100, unique=True)
    brightness = models.IntegerField(default=75)

    USERNAME_FIELD = 'arena_name'
    REQUIRED_FIELDS = []