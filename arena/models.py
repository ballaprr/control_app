from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Arena(AbstractUser):
    username = None
    email = None
    arena_name = models.CharField(max_length=100, unique=True)
    brightness = models.IntegerField(default=75)


    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    USERNAME_FIELD = 'arena_name'
    REQUIRED_FIELDS = []