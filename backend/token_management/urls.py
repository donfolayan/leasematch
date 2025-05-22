from django.urls import path, include
from .views import (
    CustomRefreshTokenView,
    CustomTokenObtainPairView,
    logout,
    is_authenticated,
)

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', logout, name='logout'),
    path('is-authenticated/', is_authenticated, name='is_authenticated'),
]