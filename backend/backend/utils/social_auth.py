from rest_framework.response import Response
from social_core.exceptions import AuthException, MissingBackend
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy, load_backend
from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

def handle_social_auth_exception(exception):
    """
    Handle exceptions that occur during social authentication.
    """
    if isinstance(exception, MissingBackend):
        return Response({'success': False, 'error': 'Invalid provider'}, status=400)
    elif isinstance(exception, AuthException):
        return Response({'success': False, 'error': str(exception)}, status=400)
    else:
        return Response({'success': False, 'error': 'An unexpected error occurred'}, status=500)

def disconnect_social_account(user, provider):
    """
    Disconnects a social account from the user.
    
    Args:
        user: The user instance to disconnect the social account from.
        provider: The name of the social provider (e.g., 'google', 'facebook').
    
    Returns:
        bool: True if the disconnection was successful, False otherwise.
    """
    try:
        # Get the UserSocialAuth instance for the given user and provider
        social_auth = UserSocialAuth.objects.get(user=user, provider=provider)

        # Check if this is the only auth method
        if not user.has_usable_password() and UserSocialAuth.objects.filter(user=user).count() == 1:
            return {'success': False, 'error': 'Cannot disconnect the only authentication method'}
        
        # Delete the UserSocialAuth instance to disconnect the account
        social_auth.delete()
        
        return {'success': True, 'message': f'{provider} account disconnected successfully'}
    except UserSocialAuth.DoesNotExist:
        return {'success': False, 'error': f'{provider} account not linked'}


def authenticate_social_user(request, provider, access_token):
    """
    Authenticate a user using social authentication.
    
    Args:
        request: The HTTP request object.
        provider: The name of the social provider (e.g., 'google', 'facebook').
        access_token: The access token obtained from the social provider.
    
    Returns:
        User: The authenticated user object.
    """
    if not provider or not access_token:
        logger.error("Missing provider or access token")
        return None

    try:
        strategy = load_strategy(request)
        backend = load_backend(strategy, provider, redirect_uri=None)
        user = backend.do_auth(access_token)

        if user:
            return user
        return None
    except MissingBackend:
        logger.error(f"Provider '{provider}' is not supported.")
        raise Exception(f"Provider '{provider}' is not supported.")
    except AuthException as e:
        logger.error(f"Authentication exception: {str(e)}")
        raise Exception("Invalid credentials or authentication failed.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            logger.error("Invalid credentials provided.")
            raise Exception("Invalid credentials provided.")
        logger.error(f"Unexpected HTTP error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in authenticate_social_user: {str(e)}")
        raise