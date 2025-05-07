from django.urls import path, include
from .views import (
    disconnect_social_account,
    social_auth,
)

urlpatterns = [
    path('social/<str:provider>/', social_auth, name='social_auth'),
    path('social/', include('social_django.urls', namespace='social')),
    path('disconnect_social_account/', disconnect_social_account, name='disconnect_social_account'),
]