from django.urls import path, include
from .views import (
    register, 
    verify_otp, 
    resend_otp,
    forgot_password,
    reset_password,
    verify_password_reset_otp,
    change_password,
    reactivate_account,
    )

urlpatterns = [
    path('register/', register, name='register'),
    path('register/verify_otp/', verify_otp, name='verify_otp'),
    path('register/resend_otp/', resend_otp, name='resend_otp'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password/', reset_password, name='reset_password'),
    path('verify_password_reset/', verify_password_reset_otp, name='verify_password_reset_otp'),
    path('change_password/', change_password, name='change_password'),
    path('reactivate_account/', reactivate_account, name='reactivate_account'),
]