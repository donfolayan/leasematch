from rest_framework import serializers
from .models import AgentProfile, LandlordProfile, TenantProfile
from .utils import NIGERIAN_STATES, PROPERTY_TYPE_CHOICES, INTERVAL_CHOICES
import datetime
import numbers
from decimal import Decimal
      
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
        if value is not None and not isinstance(value, str):
            raise serializers.ValidationError("Agency name must be a string.")
        return value
    
    def validate_agency_address(self, value):
            """
            Validate the agency address.
            """
            if value is not None and not isinstance(value, str):
                raise serializers.ValidationError("Agency address must be a string.")
            return value
    
    def validate_service_areas(self, value):
        """
        Validate the service areas.
        """
        if value is not None and not isinstance(value, list):
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
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("Service states must be a list.")
        for state in value:
            if state not in valid_states:
                raise serializers.ValidationError(f"Invalid state: {state}. Choose from {valid_states}.")
        return value
    
    def validate_agency_registration_number(self, value):
        """
        Validate the agency registration number.
        """
        if value is not None and not isinstance(value, str):
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
            if value is not None:
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
        if value is not None:
            if isinstance(value, list):
                for item in value:
                    if item not in valid_choices:
                        raise serializers.ValidationError(f"Invalid property type: {item}. Choose from {valid_choices}.")
            else:
                if value not in valid_choices:
                    raise serializers.ValidationError(f"Invalid property type: {value}. Choose from {valid_choices}.")
        return value
    
    def validate_budget(self, value):
        """
        Validate the budget.
        """
        if value is not None:
            if not isinstance(value, numbers.Number):
                raise serializers.ValidationError("Budget must be a number.")
            if value <= 0:
                raise serializers.ValidationError("Budget must be a positive number.")
        return value
    
    def validate_preferred_location(self, value):
        """
        Validate the preferred location.
        """
        if value is not None:
            if not isinstance(value, str):
                raise serializers.ValidationError("Preferred location must be a string.")
        return value
    
    def validate_move_in_date(self, value):
        """
        Validate move-in date.
        """
        if value is not None:
            if not isinstance(value, datetime.date):
                raise serializers.ValidationError("Move-in date must be a date.")
            if value < datetime.date.today():
                raise serializers.ValidationError("Move-in date cannot be in the past.")  
            return value
    
    def validate_lease_duration(self, value):
        """
        Validate lease duration.
        """
        if value is not None:
            if not isinstance(value, int):
                raise serializers.ValidationError("Lease duration must be a number.")
            if value <= 0:
                raise serializers.ValidationError("Lease duration must be a positive number.")
        return value
    
    def validate_lease_interval(self, value):
            """
            Validate lease interval.
            """
            valid_choices = [choice[0] for choice in INTERVAL_CHOICES]
            if value is not None and value not in valid_choices:
                raise serializers.ValidationError(f"Invalid lease interval. Choose from {valid_choices}.")
            return value