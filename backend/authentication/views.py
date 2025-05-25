from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from backend.utils.email import send_email
from backend.utils.otp import generate_otp
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser
from .serializer import UserRegistrationSerializer
import logging
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

User = get_user_model()

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
            otp, expiration = generate_otp()
            cache.set(f'otp_{user.id}', otp, timeout=expiration)

            # Send email
            try:
                send_email(
                    subject='Your OTP Code',
                    message=f'Your OTP code is {otp}. It will expire in 5 minutes.',
                    recipient_list=[user.email],
                )
            except Exception as e:
                logger.error(f"Email sending failed: {e}")
                return Response({"success": False, "error":f"Failed to send email:{str(e)}"}, status=500)

            return Response({
                'success': True,
                'message': 'User registered successfully. Please check your email for the OTP.',
                'user_id': user.id
            }, status=201)
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            transaction.set_rollback(True)
            return Response({'success': False, 'error': str(e)}, status=500)
    else:
        logger.error(f"Serializer errors: , {serializer.errors}")
    return Response({'success': False, 'errors': serializer.errors}, status=400)

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
        otp, expiration = generate_otp()
        cache.set(f'otp_{user.id}', otp, timeout=expiration)

        try:
        # Send email
            send_email(
                subject='Your OTP Code',
                message=f'Your new OTP code is {otp}. It will expire in 5 minutes.',
                recipient_list=[user.email],
            )
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return Response({"success": False, "error":f"Failed to send email:{str(e)}"}, status=500)

        return Response({'success': True, 'message': 'New OTP sent successfully'})
    except CustomUser.DoesNotExist:
        return Response({'success': False, 'error': 'User not found'}, status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email')

    if not email:
        return Response({'success': False, 'error': 'Email is required'}, status=400)

    try:
        user = CustomUser.objects.get(email=email)

        # Generate otp
        otp, expiration = generate_otp()
        cache.set(f'otp_{user.id}', otp, timeout=expiration)  # Store OTP in cache for 5 minutes

        # Send email with the reset link
        try:
            send_email(
                subject='Your Password Reset OTP',
                message=f'Your OTP for password reset is {otp}. It will expire in 5 minutes.',
                recipient_list=[email],
            )
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return Response({"success": False, "error":f"Failed to send email:{str(e)}"}, status=500)

        return Response({'success': True, 'message': 'Password reset email sent successfully.'})

    except CustomUser.DoesNotExist:
        return Response({'success': False, 'error': 'User with this email does not exist.'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response({'success': False, 'error': 'Missing current password or new password'}, status=400)
    
    #Verify current password
    if not check_password(current_password, user.password):
        return Response({'success': False, 'error': 'Current password is incorrect'}, status=400)
    
    # Validate new password
    try:
        validate_password(new_password, user=user)
    except ValidationError as e:
        return Response({'success': False, 'error': str(e)}, status=400)
    
    # Set new password
    user.set_password(new_password)
    user.save()

    # Invalidate all tokens for the user
    try:
        OutstandingToken.objects.filter(user=user).delete()  
    except Exception as e:
        logger.warning(f"Could not invalidate tokens for user {user.id}: {e}")

    return Response({'success': True, 'message': 'Password changed successfully'})

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_password_reset_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({'success': False, 'error': 'Missing email or otp'}, status=400)

    try:
        user = CustomUser.objects.get(email=email)
        cached_otp = cache.get(f'otp_{user.id}')

        if cached_otp and cached_otp == str(otp):
            # OTP is valid
            return Response({'success': True, 'message': 'OTP verified successfully'})
        else:
            return Response({'success': False, 'error': 'Invalid or expired OTP'}, status=400)

    except CustomUser.DoesNotExist:
        return Response({'success': False, 'error': 'User with this email does not exist.'}, status=404)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def send_activation_token(request):
    email = request.data.get('email')
    if not email:
        return Response({'success': False, 'error': 'Missing email'}, status=400)
    try:
        user = CustomUser.objects.get(email=email)
        if user.is_active:
            return Response({'success': False, 'error': 'Account already active'}, status=400)
        token = default_token_generator.make_token(user)
        response = redirect(settings.FRONTEND_URL + '/api/authentication/activate_account/')
        # Set token and user_id in cookie
        response.set_cookie(
            key='activation_token',
            value=token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=300
        )
        response.set_cookie(
            key='activation_user_id',
            value=str(user.id),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=300
        )
        response.status_code = 302
        return response
    except CustomUser.DoesNotExist:
        return Response({'success': False, 'error': 'User not found'}, status=404)

@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def activate_account(request):
    activation_user_id = request.COOKIES.get('activation_user_id')
    activation_token = request.COOKIES.get('activation_token')

    if not activation_user_id or not activation_token:
        return Response({'success': False, 'error': 'Missing user_id or token'}, status=400)

    try:
        user = CustomUser.objects.get(id=activation_user_id)
        if default_token_generator.check_token(user, activation_token):
            user.is_active = True
            user.save()
            response = Response({'success': True, 'message': 'Account activated successfully'})
            try:
                send_email(
                    subject='Account Activation Successful',
                    message='Your account has been activated successfully.',
                    recipient_list=[user.email],
                )
            except Exception as e:
                logger.error(f"Email sending failed: {e}")
            # Clear cookies
            response.delete_cookie('activation_token')
            response.delete_cookie('activation_user_id')
            return response
        else:
            return Response({'success': False, 'error': 'Invalid or expired token'}, status=400)
    except CustomUser.DoesNotExist:
        return Response({'success': False, 'error': 'User not found'}, status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not email or not new_password:
        return Response({'success': False, 'error': 'Missing email or new password'}, status=400)
    
    try:
        user = CustomUser.objects.get(email=email)
        # Validate new password
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({'success': False, 'error': str(e)}, status=400)
        # Set new password
        user.set_password(new_password)
        user.save()

        # Clear OTP from cache
        cache.delete(f'otp_{user.id}')

        return Response({'success': True, 'message': 'Password reset successfully'})
    except CustomUser.DoesNotExist:
        return Response({'success': False, 'error': 'User with this email does not exist.'}, status=404)