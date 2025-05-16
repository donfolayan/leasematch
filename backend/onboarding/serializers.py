from rest_framework import serializers
from .models import AgentProfile, LandlordProfile, TenantProfile
from .utils import NIGERIAN_STATES, PROPERTY_TYPE_CHOICES
import datetime
      
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
        def validate_agency_name(self, value):
            """
            Validate the agency name.
            """
            if type(value) != str:
                raise serializers.ValidationError("Agency name must be a string.")
            return value
        
        def validate_agency_address(self, value):
                """
                Validate the agency address.
                """
                if type(value) != str:
                    raise serializers.ValidationError("Agency address must be a string.")
                return value
        
        def validate_service_areas(self, value):
            """
            Validate the service areas.
            """
            if not isinstance(value, list):
                raise serializers.ValidationError("Service areas must be a list.")
            for area in value:
                if not isinstance(area, str):
                    raise serializers.ValidationError("Each service area must be a string.")
            return value
        
        def validate_service_states(self, value):
            """
            Validate the service states.
            """
            valid_states = [choice[0] for choice in NIGERIAN_STATES]
            if not isinstance(value, list):
                raise serializers.ValidationError("Service states must be a list.")
            for state in value:
                if state not in valid_states:
                    raise serializers.ValidationError(f"Invalid state: {state}. Choose from {valid_states}.")
            return value
        
        def validate_agency_registration_number(self, value):
            """
            Validate the agency registration number.
            """
            if not isinstance(value, str):
                raise serializers.ValidationError("Agency registration number must be a string.")
            if len(value) < 5:
                raise serializers.ValidationError("Agency registration number must be at least 5 characters long.")
            return value

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

        def validate_documents(self, value):
            """
            Validate the documents field.
            """
            max_size = 5 * 1024 * 1024
            if value and hasattr(value, 'size') and value.size > max_size:
                raise serializers.ValidationError("File size exceeds the limit of 5MB.")

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
                'lease_interval',
        ]
        read_only_fields = ['user']

        def validate_preferred_property_type(self, value):
            """
            Validate the preferred property type.
            """
            valid_choices = [choice[0] for choice in PROPERTY_TYPE_CHOICES]
            if value not in valid_choices:
                raise serializers.ValidationError(f"Invalid property type. Choose from {valid_choices}.")
            return value
        
        def validate_budget(self, value):
            """
            Validate the budget.
            """
            if value <= 0:
                raise serializers.ValidationError("Budget must be a positive number.")
            if type(value) not in [int, float]:
                raise serializers.ValidationError("Budget must be a number.")
            return value
        
        def validate_preferred_location(self, value):
            """
            Validate the preferred location.
            """
            if not value:
                raise serializers.ValidationError("Preferred location cannot be empty.")
            elif type(value) != str:
                raise serializers.ValidationError("Preferred location must be a string.")
            return value
        
        def validate_move_in_date(self, value):
            """
            Validate move-in date.
            """
            if value < datetime.date.today():
                raise serializers.ValidationError("Move-in date cannot be in the past.")
            if type(value) != datetime.date:
                raise serializers.ValidationError("Move-in date must be a date.")
            return value
        
        def validate_lease_duration(self, value):
            """
            Validate lease duration.
            """
            if value <= 0:
                raise serializers.ValidationError("Lease duration must be a positive number.")
            if type(value) != int:
                raise serializers.ValidationError("Lease duration must be a number.")
            return value
        
        def validate_lease_interval(self, value):
            """
            Validate lease interval.
            """
            valid_choices = [choice[0] for choice in TenantProfile.INTERVAL_CHOICES]
            if value not in valid_choices:
                raise serializers.ValidationError(f"Invalid lease interval. Choose from {valid_choices}.")
            return value