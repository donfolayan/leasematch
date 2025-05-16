from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from authentication.models import CustomUser


class LandlordProfile(models.Model):
    user=models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='landlord_profile')
    documents = CloudinaryField('landlord_documents/', null=True, blank=True)

class AgentProfile(models.Model):
    NIGERIAN_STATES = (
    ('abia', 'Abia'),
    ('adamawa', 'Adamawa'),
    ('akwa_ibom', 'Akwa Ibom'),
    ('anambra', 'Anambra'),
    ('bauchi', 'Bauchi'),
    ('bayelsa', 'Bayelsa'),
    ('benue', 'Benue'),
    ('borno', 'Borno'),
    ('cross_river', 'Cross River'),
    ('delta', 'Delta'),
    ('ebonyi', 'Ebonyi'),
    ('edo', 'Edo'),
    ('ekiti', 'Ekiti'),
    ('enugu', 'Enugu'),
    ('gombe', 'Gombe'),
    ('imo', 'Imo'),
    ('jigawa', 'Jigawa'),
    ('kaduna', 'Kaduna'),
    ('kano', 'Kano'),
    ('katsina', 'Katsina'),
    ('kebbi', 'Kebbi'),
    ('kogi', 'Kogi'),
    ('kwara', 'Kwara'),
    ('lagos', 'Lagos'),
    ('nasarawa', 'Nasarawa'),
    ('niger', 'Niger'),
    ('ogun', 'Ogun'),
    ('ondo', 'Ondo'),
    ('osun', 'Osun'),
    ('oyo', 'Oyo'),
    ('plateau', 'Plateau'),
    ('rivers', 'Rivers'),
    ('sokoto', 'Sokoto'),
    ('taraba', 'Taraba'),
    ('yobe', 'Yobe'),
    ('zamfara', 'Zamfara'),
    ('fct', 'Federal Capital Territory (FCT)'),
)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='agent_profile')
    agency_name = models.CharField(max_length=255)
    agency_address = models.CharField(max_length=255)
    service_areas = models.JSONField(null=True, blank=True)
    service_states = models.CharField(max_length=50, choices=NIGERIAN_STATES, null=True, blank=True)
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
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='tenant_profile')
    preferred_property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    preferred_location = models.CharField(max_length=255)
    move_in_date = models.DateField(null=True, blank=True)
    lease_duration = models.IntegerField(null=True, blank=True)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'landlord':
            LandlordProfile.objects.create(user=instance)
        elif instance.user_type == 'agent':
            AgentProfile.objects.create(user=instance)
        elif instance.user_type == 'tenant':
            TenantProfile.objects.create(user=instance)