from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Note

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
            user_type=validated_data['user_type']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email']


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model=Note
        fields=['id','description']