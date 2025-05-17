from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
import logging

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):

        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')

            res = Response()
            res.data = {'success': True, 'access': access_token, 'refresh': refresh_token}

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
            )

            res.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
            )

            return res
        
        except Exception as e:
            logger.error(f"Error in CustomTokenObtainPairView: {str(e)}")
            return Response({'success': False})

class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):

        try:
            refresh_token = request.COOKIES.get('refresh_token')
            logger.debug(f"Refresh token from cookie: {refresh_token}")
            request_data = request.data.copy()
            request_data['refresh'] = refresh_token
            request._full_data = request_data  # Patch the DRF request object

            response = super().post(request, *args, **kwargs)

            tokens = response.data
            access_token = tokens.get('access')
            new_refresh_token = tokens.get('refresh')
            

            res = Response()
            res.data = {'refreshed': True, 'access': access_token}

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
            )

            if new_refresh_token:
                new_refresh_token = tokens.get('refresh')
                res.set_cookie(
                    key='refresh_token',
                    value=new_refresh_token,
                    httponly=True,
                    secure=True,
                    samesite='None',
                    path='/',
                )

            return res
        
        except Exception as e:
            logger.error(f"Error in CustomRefreshTokenView: {str(e)}")
            return Response({'refreshed': False})
        
@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        refresh_token = request.data.get('refresh') or request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"success": False, 
                             "message": "Refresh token not provided."}, 
                             status=400)
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        res = Response({"success": True, 
                        "message": "Successfully logged out."}, 
                        status=200)
        #clear cookies
        res.delete_cookie('access_token', path='/')
        res.delete_cookie('refresh_token', path='/')
        return res
    except Exception as e:
        return Response({"success": False, 
                         "message": str(e)},
                         status=400)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_authenticated(request):
    return Response({'is_authenticated': True})