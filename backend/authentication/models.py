from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

AUTH_USER_MODEL = settings.AUTH_USER_MODEL

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
        ('agent', 'Agent'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='tenant')