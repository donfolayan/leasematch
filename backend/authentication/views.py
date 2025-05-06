from django.contrib.auth import get_user_model
from .serializer import UserRegistrationSerializer
from social_django.utils import load_strategy, load_backend
from django.views.decorators.csrf import csrf_exempt
from social_core.exceptions import AuthException, MissingBackend

from django.utils.timezone import now
import pyotp
from django.core.cache import cache
from .models import CustomUser
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


User = get_user_model()

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
@transaction.atomic
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            user.is_active = False  # Until email is verified
            user.save()

            # Generate OTP
            totp = pyotp.TOTP(pyotp.random_base32())
            otp = totp.now() #Generate time-based OTP

            cache.set(f'otp_{user.id}', otp, timeout=300)  # Store OTP in cache for 5 minutes

            # Send email
            send_mail(
                subject='Your OTP Code',
                message=f'Your OTP code is {otp}. It will expire in 5 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            return Response({
                'success': True,
                'message': 'User registered successfully. Please check your email for the OTP.',
                'user_id': user.id
            })
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'success': False, 'error': str(e)}, status=500)
    return Response({'success': False, 'errors': serializer.errors})


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    user_id = request.data.get('user_id')
    otp = request.data.get('otp')

    if not user_id or not otp:
        return Response({'success': False, 'error': 'Missing user_id or otp'}, status=400)
    
    try:
        user=CustomUser.objects.get(id=user_id)
        cached_otp = cache.get(f'otp_{user.id}')

        if cached_otp and cached_otp == str(otp):
            user.is_active = True # Activate user after OTP verification
            user.save()
            cache.delete(f'otp_{user.id}')  # Remove OTP from cache
            return Response({'success': True, 'message': 'OTP verified successfully'})
        else:
            return Response({'success': False, 'error': 'Invalid or expired OTP'}, status=400)

    except CustomUser.DoesNotExist:
        return Response({'success': False, 'error': 'User not found'}, status=404)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    user_id = request.data.get('user_id')

    if not user_id:
        return Response({'success': False, 'error': 'Missing user_id'}, status=400)
    
    try:
        user = CustomUser.objects.get(id=user_id)

        # Generate new OTP
        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()  # Generate time-based OTP

        cache.set(f'otp_{user.id}', otp, timeout=300)  # Store OTP in cache for 5 minutes

        # Send email
        send_mail(
            subject='Your OTP Code',
            message=f'Your new OTP code is {otp}. It will expire in 5 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response({'success': True, 'message': 'New OTP sent successfully'})
    except CustomUser.DoesNotExist:
        return Response({'success': False, 'error': 'User not found'}, status=404)


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