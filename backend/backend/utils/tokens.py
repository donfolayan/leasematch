from rest_framework_simplejwt.tokens import RefreshToken

def generate_token_for_user(user):
    """
    Generate a JWT token for the given user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }