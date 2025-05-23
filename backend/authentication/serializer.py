from django.db import transaction
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework import serializers
from onboarding.utils import USER_TYPE_CHOICES
from .models import UserType
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(
        choices=[choice[0] for choice in USER_TYPE_CHOICES],
        default='tenant',
    )
    class Meta:
        model=User
        fields=['id','username','email','password', 'first_name','last_name', 'user_type']
    
    @transaction.atomic
    def create(self, validated_data):
        user_type = validated_data.pop('user_type')

        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()

        # User_type
        user_type_obj, _ = UserType.objects.get_or_create(name=user_type)

        # Add user to group and user_type
        group = Group.objects.get(name=user_type)
        user.user_type.add(user_type_obj)
        user.groups.add(group)

        return user
    
    def validate(self, data):
        errors = {}
        username = data.get('username')
        email = data.get('email')

        # existing_users = User.objects.filter(Q(username=username) | 
        #                                     Q(email=email)
        #                                     ).values_list('username', 'email')
        # for existing_username, existing_email in existing_users:
        #     if existing_username == username:
        #         errors['username'] = "Username already exists"
        #     if existing_email == email:
        #         errors['email'] = "Email already exists"

        if email and "+" in email:
            raise serializers.ValidationError("Email cannot contain '+' character.")
        if username and not username.isalnum():
            raise serializers.ValidationError("Username can only contain alphanumeric characters.")
        if errors:
            raise serializers.ValidationError(errors)
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email']
