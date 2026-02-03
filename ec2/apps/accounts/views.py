import secrets
import urllib.parse

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .backends import verify_google_id_token
from .serializers import UserSerializer


class MeView(generics.RetrieveUpdateAPIView):
    """Current user profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ============================================================
# OAuth Views
# ============================================================


class GoogleLoginView(APIView):
    """Generate Google OAuth login URL.

    GET /api/accounts/oauth/login/
    - Generates OAuth URL with state token
    - Returns redirect URL or JSON with auth_url
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        request.session["oauth_state"] = state

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }

        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

        # Check if client wants JSON response
        if request.accepts("application/json") and not request.accepts("text/html"):
            return Response({"auth_url": auth_url})

        return redirect(auth_url)


class GoogleCallbackView(APIView):
    """Handle Google OAuth callback.

    GET /api/accounts/oauth/callback/
    - Receives authorization code from Google
    - Exchanges code for tokens
    - Verifies ID token
    - Creates/updates user
    - Creates session
    - Redirects to frontend
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        error = request.query_params.get("error")

        if error:
            return Response(
                {"detail": f"OAuth error: {error}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not code:
            return Response(
                {"detail": "No authorization code provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify state token
        stored_state = request.session.get("oauth_state")
        if not stored_state or state != stored_state:
            return Response(
                {"detail": "Invalid state parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        try:
            token_response = requests.post(token_url, data=token_data, timeout=10)
            token_response.raise_for_status()
            tokens = token_response.json()
        except requests.RequestException as e:
            return Response(
                {"detail": f"Token exchange failed: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify ID token
        id_token_str = tokens.get("id_token")
        if not id_token_str:
            return Response(
                {"detail": "No ID token in response."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_info = verify_google_id_token(id_token_str)
        if not user_info:
            return Response(
                {"detail": "ID token verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate (creates user if needed)
        user = authenticate(
            request,
            google_id=user_info["sub"],
            email=user_info.get("email"),
            avatar_url=user_info.get("picture"),
            name=user_info.get("name"),
        )

        if not user:
            return Response(
                {"detail": "Authentication failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create session
        login(request, user)

        # Clear OAuth state
        request.session.pop("oauth_state", None)

        # Redirect to frontend
        # TODO: Configure frontend URL via settings
        frontend_url = request.query_params.get("next", "/")
        return redirect(frontend_url)


class LogoutView(APIView):
    """Logout user.

    POST /api/accounts/logout/
    - Clears session
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Logged out successfully."})
