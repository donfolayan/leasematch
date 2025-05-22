from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework import serializers
from onboarding.utils import USER_TYPE_CHOICES
from .models import UserType

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_type = serializers.ListField(
        child=serializers.ChoiceField(choices=[choice[0] for choice in USER_TYPE_CHOICES]),
        default=['tenant'],
    )
    class Meta:
        model=User
        fields=['id','username','email','password', 'first_name','last_name', 'user_type']
    
    def create(self, validated_data):
        user_types = validated_data.pop('user_type')
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.save()

        try:
            for user_type in user_types:
                user_type_obj, created = UserType.objects.get_or_create(name=user_type)
                user.user_type.add(user_type_obj)

                group = Group.objects.get(name=user_type)
                user.groups.add(group)
        except Exception as e:
            user.delete()
            raise serializers.ValidationError(f"Error creating user type: {e}")
        return user

        
    def validate_user_type(self, value):
        
        if not isinstance(value, list):
            raise serializers.ValidationError("User type must be a list.")
        if len(value) == 0:
            value.append('tenant')
        valid_types = [choice[0] for choice in USER_TYPE_CHOICES]
        for user_type in value:
            if user_type not in valid_types:
                raise serializers.ValidationError(f"Invalid user type: {user_type}. Choose from {valid_types}.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        if not value.isalnum():
            raise serializers.ValidationError("Username must be alphanumeric")
        if not value:
            raise serializers.ValidationError("Username cannot be empty")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        if '+' in value:
            raise serializers.ValidationError("Email cannot contain '+'")
        return value

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email']
