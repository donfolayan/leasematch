from django.urls import path, include
from .views import (
    register, 
    verify_otp, 
    resend_otp,
    forgot_password,
    reset_password,
    verify_password_reset_otp,
    change_password,
    send_activation_token,
    activate_account,
    )

urlpatterns = [
    path('register/', register, name='register'),
    path('register/verify_otp/', verify_otp, name='verify_otp'),
    path('register/resend_otp/', resend_otp, name='resend_otp'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('verify-password-reset/', verify_password_reset_otp, name='verify_password_reset_otp'),
    path('change-password/', change_password, name='change_password'),
    path('send-activation-token/', send_activation_token, name='send_activation_token'),
    path('activate-account/', activate_account, name='activate_account'),
]