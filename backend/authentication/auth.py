import logging
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)

class CookiesJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header:
            raw_token = self.get_raw_token(header)
        else:
            # Fallback to cookies
            raw_token = request.COOKIES.get('access_token')

        if not raw_token:
            logger.info("No access token found in Authorization header or cookies.")
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            logger.info("Access token validated successfully.")
            return self.get_user(validated_token), validated_token
        except Exception as e:
            logger.error(f"Error validating access token: {str(e)}")
            return None