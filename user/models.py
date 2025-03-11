from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(max_length=100, unique=True, blank=False)
    password = models.CharField(
        max_length=100, blank=False, validators=[MinLengthValidator(12)]
    )
    username = models.CharField(max_length=100, blank=False, unique=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    is_admin = models.BooleanField(default=False, blank=False)
    email_verified = models.BooleanField(default=False, blank=False)
    admin_verified = models.BooleanField(default=False, blank=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']