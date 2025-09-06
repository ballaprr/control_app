from django.db import models
from user.models import User

# Create your models here.
class Arena(models.Model):
    #username = None
    #email = None
    arena_name = models.CharField(max_length=100, unique=True)
    brightness = models.IntegerField(default=75)
    active_controller = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='active_controller')

"""
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    USERNAME_FIELD = 'arena_name'
    REQUIRED_FIELDS = []
"""