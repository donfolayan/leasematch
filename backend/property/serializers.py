from rest_framework import serializers
from .models import Property
from onboarding.utils import NIGERIAN_STATES

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

        def validate_rent_price(self, data):
            """
            Validate that the rent price is a positive number.
            """
            if data <= 0:
                raise serializers.ValidationError("Rent price must be a positive number.")
            return data
        
        def validate_bedroom(self, data):
            """
            Validate that the number of bedrooms is a positive integer.
            """
            if data < 0:
                raise serializers.ValidationError("Number of bedrooms must be a positive integer.")
            return data
  