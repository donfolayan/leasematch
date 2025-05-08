from .views import (
    GoogleLogin,
    disconnect_social_account,
)
from django.urls import path, include
from dj_rest_auth.registration.views import (
    SocialAccountListView, SocialAccountDisconnectView,
)


urlpatterns = [
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('socialaccounts/<int:pk>/disconnect/', SocialAccountDisconnectView.as_view(), name='social_account_disconnect'),
    path('socialaccounts/', SocialAccountListView.as_view(), name='social_account_list'),
    path('disconnect/<str:provider>/', disconnect_social_account, name='disconnect_social_account'),
]