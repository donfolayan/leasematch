from social_core.exceptions import AuthException
from social_django.models import UserSocialAuth
from .models import CustomUser


def link_to_existing_user(backend, details, user=None, *args, **kwargs):
    """
    Link a social account to an existing user if the email matches.
    """
    if user:
        return  # User is already authenticated

    email = details.get('email')
    if email:
        try:
            existing_user = CustomUser.objects.get(email=email)
            # Check if the social account is already linked
            if not UserSocialAuth.objects.filter(user=existing_user, provider=backend.name).exists():
                return {'user': existing_user}
        except CustomUser.DoesNotExist:
            pass
    else:
        raise AuthException(backend, 'Email is required to link accounts')
    
def prevent_duplicate_social_auth(backend, uid, user=None, *args, **kwargs):
    """
    Prevent linking a social account that is already linked to another user.
    """
    if user:
        return  # Skip if the user is already authenticated

    try:
        existing_social_auth = UserSocialAuth.objects.get(uid=uid, provider=backend.name)
        if existing_social_auth.user != user:
            raise AuthException(backend, 'This social account is already linked to another user.')
    except UserSocialAuth.DoesNotExist:
        pass