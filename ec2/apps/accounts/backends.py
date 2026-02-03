from django.contrib.auth import get_user_model

User = get_user_model()


class GoogleOAuthBackend:
    """Authenticate users via Google OAuth token info."""

    def authenticate(self, request, google_id=None, email=None, **kwargs):
        if google_id is None:
            return None
        try:
            user = User.objects.get(google_id=google_id)
        except User.DoesNotExist:
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
