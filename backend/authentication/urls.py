from django.urls import path, include
from .views import CustomTokenObtainPairView, CustomRefreshTokenView, logout, is_authenticated, register, social_auth

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', logout, name='logout'),
    path('is_authenticated/', is_authenticated, name='is_authenticated'),
    path('register/', register, name='register'),
    path('social_auth/', social_auth, name='social_auth'),
    path('social/', include('social_django.urls', namespace='social')),  # Include social auth URLs
]