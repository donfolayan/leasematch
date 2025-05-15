from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import AgentProfileSerializer, LandlordProfileSerializer, TenantProfileSerializer

ONBOARDING_STEPS = {
    'landlord': {
        1: 'Add profile details',
        2: 'Add first property',
        3: 'Complete onboarding',
    },
    'agent': {
        1: 'Add profile details',
        2: 'Add first property',
        3: 'Complete onboarding',
    },
    'tenant': {
        1: 'Set preferences',
        2: 'Complete onboarding',
    },
}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_agent_profile(request):
    """
    Endpoint to update agent profile.
    """
    user = request.user
    if user.user_type != 'agent':
        return Response({"message": "Invalid User Type"}, status=403)
    data = request.data
    agent_profile = user.agent_profile
    serializer = AgentProfileSerializer(agent_profile, data=data, partial=True)
    if serializer.is_valid():
        agent_profile = serializer.save()
        return Response({"success": True, "message": "Agent Profile Successfully Updated", "profile_id": agent_profile.id}, status=200)
    else:
        return Response({"success": False, "message": "Agent Profile Not Updated", "errors": serializer.errors}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_landlord_profile(request):
    """
    Endpoint to update landlord profile.
    """
    user = request.user
    if user.user_type != 'landlord':
        return Response({"message": "Invalid User Type"}, status=403)
    data = request.data
    landlord_profile = user.landlord_profile
    serializer = LandlordProfileSerializer(landlord_profile, data=data, partial=True)
    if serializer.is_valid():
        landlord_profile = serializer.save()
        return Response({"success": True, "message": "Landlord Profile Successfully Updated", "profile_id": landlord_profile.id}, status=200)
    else:
        return Response({"success": False, "message": "Landlord Profile Not Updated", "errors": serializer.errors}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_tenant_profile(request):
    """
    Endpoint to update tenant profile.
    """
    user = request.user
    if user.user_type != 'tenant':
        return Response({"message": "Invalid User Type"}, status=403)
    data = request.data
    tenant_profile = user.tenant_profile
    serializer = TenantProfileSerializer(tenant_profile, data=data, partial=True)
    if serializer.is_valid():
        tenant_profile = serializer.save()
        return Response({"success": True, "message": "Tenant Profile Successfully Updated", "profile_id": tenant_profile.id}, status=200)
    else:
        return Response({"success": False, "message": "Tenant Profile Not Updated", "errors": serializer.errors}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_onboarding_status(request):
    user = request.user
    user_type = user.user_type
    current_step = user.onboarding_step

    steps = ONBOARDING_STEPS.get(user_type, {})
    next_action = steps.get(current_step, "Onboarding Complete")

    return Response({
        "user_type": user_type,
        "current_step": current_step,
        "next_action": next_action,
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_onboarding_step(request):
    user = request.user
    next_step = request.data.get('next_step')

    if not next_step:
        return Response({"success": False, "message": "Next step not provided."}, status=400)
    
    user.onboarding_step = next_step
    user.save()
    return Response({"success": True, "message": "Onboarding step updated successfully."}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_onboarding(request):
    user = request.user
    
    if user.onboarding_step != max(ONBOARDING_STEPS[user.user_type].keys()):
        return Response({"success": False, "message": "Onboarding not complete."}, status=400)
    user.is_onboarded = True
    user.save()
    return Response({"success": True, "message": "Onboarding completed successfully."}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def skip_onboarding(user):
    """
    Function to skip onboarding for a user.
    """
    user.is_onboarded = True
    user.onboarding_step = max(ONBOARDING_STEPS[user.user_type].keys())
    user.save()
