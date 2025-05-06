import uuid
from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser

AUTH_USER_MODEL = settings.AUTH_USER_MODEL

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
        ('agent', 'Agent'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='tenant')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def generate_otp(self):
        import pyotp
        otp = pyotp.TOTP(pyotp.random_base32()).now()
        self.otp = otp
        self.otp_expiration = datetime.now() + timedelta(minutes=5)  # OTP valid for 5 minutes
        self.save()
        return otp