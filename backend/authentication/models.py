import uuid
from django.db import models
from django.conf import settings
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from backend.utils.otp import generate_otp
from django.utils.timezone import now

AUTH_USER_MODEL = settings.AUTH_USER_MODEL

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
        ('agent', 'Agent'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='tenant')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_onboarded = models.BooleanField(default=False)
    onboarding_step = models.IntegerField(default=0)

    def generate_otp(self):
        otp, expiration = generate_otp()
        self.otp = otp
        self.otp_expiration = expiration  # OTP valid for 5 minutes
        self.save()
        return otp

def default_scheduled_time():
    return now() + timedelta(days=7)
    
class ScheduledDeletion(models.Model):
    DELETION_TYPE_CHOICES = (
        ('user', 'User Account'),
        ('social_account', 'Social Auth Account'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    social_account = models.OneToOneField('socialaccount.SocialAccount', on_delete=models.CASCADE, null=True, blank=True)
    deletion_type = models.CharField(max_length=20, choices=DELETION_TYPE_CHOICES)
    scheduled_for = models.DateTimeField(default=default_scheduled_time)
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        if self.deletion_type == 'user':
            return f"Scheduled deletion for user {self.user.email} at {self.scheduled_for}"
        elif self.deletion_type == 'social_account':
            if self.social_account:
                return f"Scheduled deletion for social auth {self.social_account.provider} for {self.user.email} at {self.scheduled_for}"
            else:
                return f"Scheduled deletion for social auth for {self.user.email} at {self.scheduled_for}"
        elif self.deletion_type == 'inactive_user':
            return f"Scheduled deletion for inactive user {self.user.email} at {self.scheduled_for}"
        
