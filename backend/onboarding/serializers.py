from rest_framework import serializers
from .models import AgentProfile, LandlordProfile, TenantProfile
      
class AgentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the AgentProfile model.
    """
    class Meta:
        model = AgentProfile
        fields = [
                'user',
                'agency_name',
                'agency_address',
                'service_areas',
                'service_states',
                'agency_registration_number',
        ]
        read_only_fields = ['user']

class LandlordProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the LandlordProfile model.
    """
    class Meta:
        model = LandlordProfile
        fields = [
                'user',
                'documents',
        ]
        read_only_fields = ['user']

class TenantProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the TenantProfile model.
    """
    class Meta:
        model = TenantProfile
        fields = [
                'user',
                'preferred_property_type',
                'budget',
                'preferred_location', 
                'move_in_date',
                'lease_duration',
        ]
        read_only_fields = ['user']