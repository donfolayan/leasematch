from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from authentication.models import CustomUser


class LandlordProfile(models.Model):
    user=models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='landlord_profile')
    documents = CloudinaryField('landlord_documents/', null=True, blank=True)

class AgentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='agent_profile')
    agency_name = models.CharField(max_length=255)
    agency_address = models.CharField(max_length=255)
    service_areas = models.JSONField(null=True, blank=True)
    service_states = models.JSONField(null=True, blank=True)
    agency_registration_number = models.CharField(max_length=100, null=True, blank=True)

class TenantProfile(models.Model):
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

    INTERVAL_CHOICES = (
        ('month', 'Month'),
        ('year', 'Year'),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='tenant_profile')
    preferred_property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    preferred_location = models.CharField(max_length=255)
    move_in_date = models.DateField(null=True, blank=True)
    lease_duration = models.IntegerField(null=True, blank=True)
    lease_interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES, null=True, blank=True, default='year')

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'landlord':
            LandlordProfile.objects.create(user=instance)
        elif instance.user_type == 'agent':
            AgentProfile.objects.create(user=instance)
        elif instance.user_type == 'tenant':
            TenantProfile.objects.create(user=instance)