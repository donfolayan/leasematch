import uuid
import logging
from django.db import models
from django.conf import settings
from datetime import timedelta
from onboarding.utils import USER_TYPE_CHOICES
from django.contrib.auth.models import AbstractUser
from backend.utils.otp import generate_otp
from django.utils.timezone import now

logger = logging.getLogger(__name__)

AUTH_USER_MODEL = settings.AUTH_USER_MODEL

class UserType(models.Model):
    name = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='tenant', unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    user_type = models.ManyToManyField(UserType, related_name='users')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    is_onboarded = models.BooleanField(default=False)
    onboarding_step = models.IntegerField(default=1)
    
    def add_user_type(self, user_type):
        try:
            if isinstance(user_type, str):
                user_type_obj, created = UserType.objects.get_or_create(name=user_type)
                self.user_type.add(user_type_obj)
            # if user_type is provided
            else:
                self.user_type.add(user_type)
            return True
        except Exception as e:
            logger.error(f"Error adding user type: {e}")
            return False

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