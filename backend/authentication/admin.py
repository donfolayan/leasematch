from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from allauth.socialaccount.models import SocialAccount
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'id', 'social_account_provider')
    list_filter = ('user_type',)
    search_fields = ('username', 'email', 'user_type')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type',)}),
    )

    def social_account_provider(self, obj):
        social_accounts = SocialAccount.objects.filter(user=obj)
        if social_accounts.exists():
            return ", ".join([social.provider for social in social_accounts])
        return 'None'

admin.site.register(CustomUser, CustomUserAdmin)
