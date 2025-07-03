import pytest
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def url():
    return reverse("google_auth_direct")


@pytest.fixture
def valid_payload():
    return {
        "provider": "google",
        "token": "valid_token"
    }


@pytest.fixture
def google_id_info():
    return {
        "email": "testuser@example.com",
        "name": "Test User"
    }


@patch("rbac.views.id_token.verify_oauth2_token")
@patch("rbac.views.User.objects.get_or_create")
def test_google_auth_success(mock_get_or_create, mock_verify_token, api_client, url, valid_payload, google_id_info):
    mock_verify_token.return_value = google_id_info

    mock_user = MagicMock()
    mock_user.email = google_id_info["email"]
    mock_user.name = google_id_info["name"]
    mock_user.username = google_id_info["email"]
    mock_user.id = 1
    mock_get_or_create.return_value = (mock_user, True)

    response = api_client.post(url, valid_payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == google_id_info["email"]
    assert data["name"] == google_id_info["name"]
    assert data["is_new_user"] is True
    assert "access_token" in data
    assert "refresh_token" in data
    assert "username" in data
    assert "userId" in data
    assert data["message"] == "User authenticated successfully"


def test_missing_provider_or_token(api_client, url):
    response = api_client.post(url, {"provider": "", "token": ""}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "provider" in response.data
    assert "token" in response.data


@patch("rbac.views.id_token.verify_oauth2_token")
def test_google_auth_missing_email(mock_verify_token, api_client, url, valid_payload):
    mock_verify_token.return_value = {"name": "No Email User"}

    response = api_client.post(url, valid_payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Google account must have an email"


@patch("rbac.views.id_token.verify_oauth2_token", side_effect=Exception("Invalid token"))
def test_invalid_token_raises_error(mock_verify_token, api_client, url, valid_payload):
    response = api_client.post(url, valid_payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Invalid token"


@patch("rbac.views.id_token.verify_oauth2_token")
@patch("rbac.views.User.objects.get_or_create")
def test_existing_user(mock_get_or_create, mock_verify_token, api_client, url, valid_payload, google_id_info):
    mock_verify_token.return_value = google_id_info

    mock_user = MagicMock()
    mock_user.email = google_id_info["email"]
    mock_user.name = google_id_info["name"]
    mock_user.username = google_id_info["email"]
    mock_user.id = 42
    mock_get_or_create.return_value = (mock_user, False)

    response = api_client.post(url, valid_payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == google_id_info["email"]
    assert data["is_new_user"] is False
