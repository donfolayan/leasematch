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
    path('agent_profile/update/', update_agent_profile, name='update-agent-profile'),
    path('landlord_profile/update/', update_landlord_profile, name='update-landlord-profile'),
    path('tenant_profile/update/', update_tenant_profile, name='update-tenant-profile'),
    path('status/', get_onboarding_status, name='get-onboarding-status'),
    path('update', update_onboarding_step, name='update-onboarding-step'),
    path('complete/', complete_onboarding, name='complete-onboarding'),
]