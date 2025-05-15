from django.db import models
from authentication.models import CustomUser

class Property(models.Model):
    USER_TYPE_CHOICES = (
        ('landlord', 'Landlord'),
        ('agent', 'Agent'),
    )
    PROPERTY_TYPE_CHOICES = (
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condo'),
        ('townhouse', 'Townhouse'),
        ('duplex', 'Duplex'),
        ('studio', 'Studio'),
        ('villa', 'Villa'),
        ('self_contained', 'Self Contained'),
        ('room and parlour', 'Room and Parlour'),
        ('shared accommodation', 'Shared Accommodation'),
        ('office space', 'Office Space'),
        ('commercial property', 'Commercial Property'),
        ('land', 'Land'),
    )
    uploader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_properties')
    uploader_user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Nigeria')
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    square_footage = models.IntegerField(null=True, blank=True)
    rent_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_from = models.DateField()
    lease_terms = models.TextField()
