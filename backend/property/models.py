from django.db import models
from authentication.models import CustomUser
from onboarding.utils import PROPERTY_TYPE_CHOICES, COUNTRY_CHOICES, SUPER_USER_TYPE_CHOICES
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import datetime

class Property(models.Model):  
    uploader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_properties')
    uploader_user_type = models.CharField(max_length=10, choices=SUPER_USER_TYPE_CHOICES)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, default='nigeria', choices=COUNTRY_CHOICES)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    bedrooms = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    bathrooms = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    square_footage = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    rent_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    available_from = models.DateField()
    lease_terms = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def clean(self):
        super().clean()
        if self.available_from and self.available_from < datetime.date.today():
            raise ValidationError({'available_from': "Available from date cannot be in the past."})
    
    def __str__(self):
        return f"{self.property_type} in {self.city}, {self.state} at {self.address}"