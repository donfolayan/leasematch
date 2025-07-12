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
    confirm_password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(
        choices=[choice[0] for choice in USER_TYPE_CHOICES],
        default='tenant',
    )
    class Meta:
        model=User
        fields=['id','username','email','password','confirm_password', 'first_name','last_name', 'user_type']
    
    @transaction.atomic
    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        validated_data.pop('confirm_password', None)
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
        group, _ = Group.objects.get_or_create(name=user_type)
        user.user_type.add(user_type_obj)
        user.groups.add(group)
        return user
    
    def validate(self, data):
        errors = {}
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        existing_users = User.objects.filter(Q(username=username) | 
                                            Q(email=email)
                                            ).values_list('username', 'email')
        for existing_username, existing_email in existing_users:
            if existing_username == username:
                errors['username'] = "Username already exists"
            if existing_email == email:
                errors['email'] = "Email already exists"
        if email and "+" in email:
            raise serializers.ValidationError("Email cannot contain '+' character.")
        if username and not username.isalnum():
            raise serializers.ValidationError("Username can only contain alphanumeric characters.")
        non_field_errors = []
        if password != confirm_password:
            non_field_errors.append("Passwords do not match.")
        if password and len(password) < 8:
            errors['password'] = ["Password must be at least 8 characters long."]
        if non_field_errors:
            errors['non_field_errors'] = non_field_errors
        if errors:
            raise serializers.ValidationError(errors)
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email']

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")
        
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid credentials.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        data['user'] = user
        return data

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        # Always return valid for any email for security
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        errors = {}
        non_field_errors = []
        if password != confirm_password:
            non_field_errors.append("Passwords do not match.")
        if password and len(password) < 8:
            errors['password'] = ["Password must be at least 8 characters long."]
        if non_field_errors:
            errors['non_field_errors'] = non_field_errors
        if errors:
            raise serializers.ValidationError(errors)
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    user_types = serializers.SerializerMethodField()
    is_onboarded = serializers.BooleanField(read_only=True)
    onboarding_step = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_types', 'is_onboarded', 'onboarding_step']
        read_only_fields = ['id', 'username']
    def get_user_types(self, obj):
        return obj.get_user_types()
    def get_onboarding_step(self, obj):
        return getattr(obj, 'onboarding_step', None)
    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
