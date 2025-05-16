from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework import serializers
from onboarding.utils import USER_TYPE_CHOICES

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['id','username','email','password', 'first_name','last_name', 'user_type']
    
    def create(self, validated_data):

        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            user_type=validated_data['user_type'],
        )
        user_type = validated_data.pop('user_type')

        user.set_password(validated_data['password'])
        user.save()

        # Assign User to a group based on user_type
        if user_type == 'landlord':
            group = Group.objects.get(name='landlord')
        elif user_type == 'tenant':
            group = Group.objects.get(name='tenant')
        elif user_type == 'agent':
            group = Group.objects.get(name='agent')
        else:
            raise serializers.ValidationError("Invalid user type")
        
        user.groups.add(group)

        return user
    
    def validate_user_type(self, value):
        if value not in USER_TYPE_CHOICES:
            raise serializers.ValidationError("Invalid user type")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email']
