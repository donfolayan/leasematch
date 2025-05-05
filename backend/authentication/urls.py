from django.urls import path
from .views import get_notes, CustomTokenObtainPairView, CustomRefreshTokenView, logout, is_authenticated

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', logout, name='logout'),
    path('is_authenticated/', is_authenticated, name='is_authenticated'),
    path('notes/', get_notes, name='get_notes'),
]