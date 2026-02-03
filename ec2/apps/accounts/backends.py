"""Google OAuth authentication backend."""

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

logger = logging.getLogger(__name__)

User = get_user_model()


class GoogleOAuthBackend:
    """Authenticate users via Google OAuth token."""

    def authenticate(self, request, google_id=None, email=None, avatar_url=None, name=None, **kwargs):
        """Authenticate user by google_id, creating if necessary."""
        if google_id is None:
            return None

        try:
            user = User.objects.get(google_id=google_id)
            # Update avatar_url if changed
            if avatar_url and user.avatar_url != avatar_url:
                user.avatar_url = avatar_url
                user.save(update_fields=["avatar_url"])
            return user
        except User.DoesNotExist:
            pass

        # Auto-create user on first login
        if email:
            # Check if user with this email already exists
            try:
                user = User.objects.get(email=email)
                # Link google_id to existing user
                user.google_id = google_id
                if avatar_url:
                    user.avatar_url = avatar_url
                user.save(update_fields=["google_id", "avatar_url"])
                return user
            except User.DoesNotExist:
                pass

            # Create new user
            username = email.split("@")[0]
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create(
                username=username,
                email=email,
                google_id=google_id,
                avatar_url=avatar_url or "",
                first_name=name.split()[0] if name else "",
                last_name=" ".join(name.split()[1:]) if name and len(name.split()) > 1 else "",
            )
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def verify_google_id_token(token: str) -> dict | None:
    """Verify Google ID token and return user info.

    Returns:
        dict with keys: sub (google_id), email, name, picture
        None if verification fails
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        # Verify issuer
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            logger.warning("Invalid token issuer: %s", idinfo["iss"])
            return None

        return {
            "sub": idinfo["sub"],
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture"),
        }
    except ValueError as e:
        logger.warning("Google ID token verification failed: %s", e)
        return None
