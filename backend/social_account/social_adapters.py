from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Prevent resetting the password when linking a social account.
        """

        user = sociallogin.user
        if user.id and user.has_usable_password():
            user.set_password(user.password)
            return
        super().pre_social_login(request, sociallogin)