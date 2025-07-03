import pytest
from django.urls import reverse, resolve
from rest_framework.test import APIClient
from rbac.views import (
    CustomLoginView,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    GoogleAuthViewSet
)
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
from rest_framework_simplejwt.views import TokenRefreshView

@pytest.mark.django_db
def test_custom_login_url_resolves():
    assert resolve("/auth/login/").func.view_class == CustomLoginView

def test_token_refresh_url_resolves():
    assert resolve("/auth/token/refresh/").func.view_class == TokenRefreshView

def test_password_reset_url_resolves():
    assert resolve("/auth/forgot-password/").func.view_class == CustomPasswordResetView

def test_password_reset_confirm_url_resolves():
    assert resolve("/auth/reset-password/").func.view_class == CustomPasswordResetConfirmView

# def test_social_login_url_resolves():
#     match = resolve("/auth/social/google/")
#     assert match.func.view_class == OAuth2LoginView
#     assert match.kwargs["provider"] == "google"


def test_social_login_url_resolves():
    match = resolve("/auth/social/google/")
    assert match.func.view_class.__name__ == "OAuth2LoginView"
    assert match.kwargs["provider"] == "google"


def test_google_auth_direct_url_resolves():
    match = resolve("/auth/google-auth/direct/")
    assert match.func.cls == GoogleAuthViewSet
    assert match.func.actions["post"] == "create"

def test_google_auth_router_url_resolves():
    match = resolve("/google-auth/")
    assert match.func.cls == GoogleAuthViewSet


client = APIClient()

def test_invalid_login_url_returns_404():
    response = client.get("/auth/login/invalid/")
    assert response.status_code == 404

def test_non_existing_route_returns_404():
    response = client.get("/non-existing/")
    assert response.status_code == 404

# import pytest
# from rest_framework.test import APIClient

# client = APIClient()

# def test_wrong_social_provider_route_returns_500():
#     response = client.get("/auth/social/unknownprovider/")
#     assert response.status_code in [400, 500]
from django.urls import reverse, resolve
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView

def test_social_login_route_resolves_for_valid_provider():
    match = resolve("/auth/social/google/")
    assert match.func.view_class == OAuth2LoginView
    assert match.kwargs["provider"] == "google"

def test_social_login_route_resolves_for_invalid_provider():
    match = resolve("/auth/social/invalid/")
    assert match.func.view_class == OAuth2LoginView
    assert match.kwargs["provider"] == "invalid"


@pytest.mark.django_db
def test_smoke_all_defined_urls():
    urls = [
        "/auth/login/",
        "/auth/token/refresh/",
        "/auth/forgot-password/",
        "/auth/reset-password/",
        "/auth/google-auth/direct/",
        "/google-auth/"
        # "/auth/social/google/",  # Skip this if adapter not configured
    ]

    client = APIClient()
    for url in urls:
        method = "post" if "login" in url or "auth" in url else "get"
        response = getattr(client, method)(url)
        assert response.status_code in [200, 400, 401, 403], f"{url} failed with {response.status_code}"

