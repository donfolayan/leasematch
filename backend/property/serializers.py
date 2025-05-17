from rest_framework import serializers
from .models import Property
import datetime
from onboarding.utils import NIGERIAN_STATES, COUNTRY_CHOICES, PROPERTY_TYPE_CHOICES
import numbers

class PropertySerializer(serializers.ModelSerializer):
    """
    Serializer for the Property model.
    """
    class Meta:
        model = Property
        fields = [
            'id',
            'uploader',
            'uploader_user_type',
            'address',
            'city',
            'state',
            'zip_code',
            'country',
            'property_type',
            'bedrooms',
            'bathrooms',
            'square_footage',
            'rent_price',
            'available_from',
            'lease_terms'
        ]
        read_only_fields = ['id', 'uploader', 'uploader_user_type']

    def validate_address(self, data):
        """
        Validate that the address is a string.
        """
        if not isinstance(data, str):
            raise serializers.ValidationError("Address must be a string.")
        return data
    
    def validate_city(self, data):
        """
        Validate that the city is a string.
        """
        if not isinstance(data, str):
            raise serializers.ValidationError("City must be a string.")
        return data
    
    def validate_state(self, data):
        """
        Validate that the state is a string.
        """
        if not isinstance(data, str):
            raise serializers.ValidationError("State must be a string.")
        valid_states = [choice[0] for choice in NIGERIAN_STATES]
        if data not in valid_states:
            raise serializers.ValidationError(f"Invalid state: {data}. Choose from {valid_states}.")
        return data

    def validate_zip_code(self, data):
        """
        Validate that the zip code is a string.
        """
        if not isinstance(data, str):
            raise serializers.ValidationError("Zip code must be a string.")
        return data
    
    def validate_country(self, data):
        """
        Validate country.
        """
        if not isinstance(data, str):
            raise serializers.ValidationError("Country must be a string.")
        valid_countries = [choice[0] for choice in COUNTRY_CHOICES]
        if data not in valid_countries:
            raise serializers.ValidationError(f"Invalid country: {data}. Choose from {valid_countries}.")
        return data
    
    def validate_property_type(self, data):
        """
        Validate property type.
        """
        if not isinstance(data, str):
            raise serializers.ValidationError("Property type must be a string.")
        valid_property_types = [choice[0] for choice in PROPERTY_TYPE_CHOICES]
        if data not in valid_property_types:
            raise serializers.ValidationError(f"Invalid property type: {data}. Choose from {valid_property_types}.")
        return data
    
    def validate_bathrooms(self, data):
        """
        Validate that the number of bathrooms is a positive integer.
        """
        if not isinstance(data, int) or data <= 0:
            raise serializers.ValidationError("Number of bathrooms must be a positive integer.")
        return data
    
    def validate_square_footage(self, data):
        """
        Validate that the square footage is a positive integer.
        """
        if not isinstance(data, int) or data <= 0:
            raise serializers.ValidationError("Square footage must be a positive integer.")
        return data
    
    def validate_available_from(self, data):
        """
        Validate that the available from date is in the future.
        """
        if data < datetime.date.today():
            raise serializers.ValidationError("Available from date must be in the future.")
        return data
    
    def validate_lease_terms(self, data):
        """
        Validate that the lease terms is a string.
        """
        if not isinstance(data, str):
            raise serializers.ValidationError("Lease terms must be a string.")
        return data

    def validate_rent_price(self, data):
        """
        Validate that the rent price is a positive number.
        """
        if not isinstance(data, (int, float, numbers.Number)) or data <= 0:
            raise serializers.ValidationError("Rent price must be a positive number.")
        return data
    
    def validate_bedrooms(self, data):
        """
        Validate that the number of bedrooms is a positive integer.
        """
        if not isinstance(data, int) or data <= 0:
            raise serializers.ValidationError("Number of bedrooms must be a positive integer.")
        return data
