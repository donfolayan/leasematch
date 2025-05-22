from django.urls import path
from .views import (
    update_agent_profile,
    update_landlord_profile,
    update_tenant_profile,
    get_onboarding_status,
    update_onboarding_step,
    complete_onboarding,
    skip_onboarding
)

urlpatterns = [
    path('agent-profile/update/', update_agent_profile, name='update_agent_profile'),
    path('landlord-profile/update/', update_landlord_profile, name='update_landlord_profile'),
    path('tenant-profile/update/', update_tenant_profile, name='update_tenant_profile'),
    path('status/', get_onboarding_status, name='get_onboarding_status'),
    path('update/', update_onboarding_step, name='update_onboarding_step'),
    path('skip/', skip_onboarding, name='skip_onboarding'),
    path('complete/', complete_onboarding, name='complete_onboarding'),
]