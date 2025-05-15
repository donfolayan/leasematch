from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from backend.utils.email import send_email
from backend.utils.deletions import schedule_deletion
from decouple import config
import logging

logger = logging.getLogger(__name__)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = config('GOOGLE_OAUTH_CALLBACK_URL')
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = self.request.user
        if user.is_authenticated:
            refresh = RefreshToken.for_user(user)
            logger.info(f"Generated tokens for user {user.id}")
            response.data['access'] = str(refresh.access_token)
            response.data['refresh'] = str(refresh)

            #set tokens in cookies
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
            )
        return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disconnect_social_account(request, provider):
    """
    Disconnect a social account if there are other social media accounts connected to the user.
    If there are no other social media accounts connected, delete the user account after 7 days.

    Args:
        request: The HTTP request object.
        provider: The social media provider to disconnect.

    Returns:
        Response: A JSON response indicating the success or failure of the operation.
    """

    # logger.info(f"Disconnecting {provider} account for user {request.user.id}")
    # if not request.user.is_authenticated:
    #     logger.error("User is not authenticated")
    #     return Response({'success': False, 'error': 'User not authenticated'}, status=401)
    
    # try:
    #     social_account = SocialAccount.objects.get(user=request.user, provider=provider)
    #     logger.info(f"Found social account for provider {provider}")
    # except SocialAccount.DoesNotExist:
    #     logger.error(f"Social account for provider {provider} does not exist")
    #     return Response({'success': False, 'error': 'Social account not found'}, status=404)

    user = request.user
    
    logger.info(f"Disconnecting {provider} account for user {request.user.id}")
    if not request.user.is_authenticated:
        logger.error("User is not authenticated")
        return Response({'success': False, 'error': 'User not authenticated'}, status=401)
    
    try:
        social_account = SocialAccount.objects.get(user=user, provider=provider) #qs of all social_account instances of the user
        other_social_accounts = SocialAccount.objects.filter(user=user).exclude(provider=provider)
        has_regular_account = user.has_usable_password() # check if the user has a regular account

        if other_social_accounts.exists() or has_regular_account:
            social_account.delete()
            return Response({
                'success': True, 
                'message': f'{provider} account disconnected successfully'
                }, status=200)
        else:
            # Schedule deletion of the user account
            schedule_deletion(user, deletion_type='user', days=7)

            # Send email to user
            send_email(
                subject="Account Deletion Scheduled",
                message="Your account is scheduled for deletion in 7 days. If you wish to cancel this deletion, please contact support.",
                recipient_list=[user.email],
            )

            return Response({'success': True, 'message': 'User account scheduled for deletion'}, status=200)
    except SocialAccount.DoesNotExist:
        return Response({
            'success': False, 
            'error': 'Social account not found'
            }, status=404)
