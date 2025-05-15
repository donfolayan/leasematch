from rest_framework import serializers
from .models import Property

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
  