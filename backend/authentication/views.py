from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import get_user_model
from social_django.utils import load_strategy, load_backend
from django.views.decorators.csrf import csrf_exempt
from social_core.exceptions import AuthException, MissingBackend
from .serializer import UserRegistrationSerializer

User = get_user_model()

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):

        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens.get('access')
            refresh_token = tokens.get('refresh')

            res = Response()
            res.data = {'success': True}

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
        
        except:
            return Response({'success': False})
        

class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):

        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)

            tokens = response.data
            access_token = tokens.get('access')
            

            res = Response()
            res.data = {'refreshed': True}

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
            )

            return res
        
        except:
            return Response({'refreshed': False})
        

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        res = Response()
        res.data = {'success': True}

        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('refresh_token', path='/', samesite='None')

        return res
    except:
        return Response({'success': False})
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_authenticated(request):
    return Response({'is_authenticated': True})



@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response({'success': False, 'errors': serializer.errors})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def social_auth(request):
    provider = request.data.get('provider')
    access_token = request.data.get('access_token')

    if not provider or not access_token:
        return Response({'success': False, 'error': 'Missing provider or access token'}, status=400)
    
    try:
        strategy = load_strategy(request)
        backend = load_backend(strategy, provider, redirect_uri=None)
        user = backend.do_auth(access_token)

        if user and user.is_active:
            #Generate a token for the user
            refresh = RefreshToken.for_user(user)
            return Response({
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        elif user and not user.is_active:
            return Response({'success': False, 'error': 'User is inactive'}, status=403)
        else:
            return Response({'success': False, 'error': 'Authentication failed'}, status=401)
            
    except MissingBackend:
        return Response({'success': False, 'error': 'Invalid provider'}, status=400)
    except AuthException as e:
        return Response({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)