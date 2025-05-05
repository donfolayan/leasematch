from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
        ('agent', 'Agent'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='tenant')

class Note(models.Model):
    description = models.CharField(max_length=300)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='note', on_delete=models.CASCADE)

    