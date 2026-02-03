from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("me/", views.MeView.as_view(), name="me"),
    # OAuth endpoints
    path("oauth/login/", views.GoogleLoginView.as_view(), name="oauth-login"),
    path("oauth/callback/", views.GoogleCallbackView.as_view(), name="oauth-callback"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
