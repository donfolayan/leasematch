from social_django.utils import load_strategy, load_backend
from django.views.decorators.csrf import csrf_exempt
from social_django.models import UserSocialAuth
from social_core.exceptions import AuthException, MissingBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from backend.utils.tokens import generate_token_for_user
from backend.utils.serializer import serialize_user
from backend.utils.social_auth import handle_social_auth_exception, disconnect_social_account as disconnect_social_account_util, authenticate_social_user
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def social_auth(request, provider):
    """
    Handle social authentication and ensure the user is activated.
    """
    access_token = request.data.get('access_token')

    if not provider or not access_token:
        return Response({'success': False, 'error': 'Missing provider or access token'}, status=400)

    try:
        # Authenticate the user using the social provider
        user = authenticate_social_user(request, provider, access_token)

        if user:
            # Ensure the user is active
            if not user.is_active:
                user.is_active = True
                user.save()

            # Generate tokens for the user
            refresh = generate_token_for_user(user)
            return Response({
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': serialize_user(user),
            }, status=200)
        else:
            return Response({'success': False, 'error': 'Authentication failed'}, status=401)
    except MissingBackend:
        logger.error(f"Provider '{provider}' is not supported.")
        return Response({'success': False, 'error': f"Provider '{provider}' is not supported"}, status=401)
    except Exception as e:
        logger.error(f"Error in social auth view: {str(e)}")
        if "Invalid credentials" in str(e):
            return Response({'success': False, 'error': 'Invalid credentials provided'}, status=401)
        return Response({'success': False, 'error': 'An unexpected error occurred'}, status=500)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disconnect_social_account(request):
    user = request.user
    provider = request.data.get('provider')

    if not provider:
        return Response({'success': False, 'error': 'Provider is required'}, status=400)

    result = disconnect_social_account_util(user, provider)
    if result['success']:
        return Response({'success': True, 'message': result['message']})
    else:
        return Response({'success': False, 'error': result['error']}, status=400)