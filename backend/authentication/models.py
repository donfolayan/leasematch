from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Note(models.Model):
    description = models.CharField(max_length=300)
    owner = models.ForeignKey(User, related_name='note', on_delete=models.CASCADE)

    