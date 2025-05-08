from django.urls import include, path

urlpatterns = [
    path('authentication/', include('authentication.urls')),
    path('account_management/', include('account_management.urls')),
    path('social_account/', include('social_account.urls')),
    path('token_management/', include('token_management.urls')),
]