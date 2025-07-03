# tests/rbac/test_custom_password_reset_confirm.py

import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status
from rbac.models import DirectUser
from django.contrib.auth.tokens import default_token_generator

import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def reset_url():
    return reverse("password_reset_confirm")


@pytest.fixture
def mock_user():
    user = MagicMock(spec=DirectUser)
    user.pk = 1
    user.set_password = MagicMock()
    user.save = MagicMock()
    return user


@patch("rbac.views.User.objects.filter")
@patch("rbac.views.default_token_generator.check_token")
def test_successful_password_reset(mock_check_token, mock_user_filter, api_client, reset_url, mock_user):
    uid = urlsafe_base64_encode(force_bytes(mock_user.pk))
    token = "valid-token"

    mock_user_filter.return_value.first.return_value = mock_user
    mock_check_token.return_value = True

    payload = {"uid": uid, "token": token, "new_password": "NewStrongPass123!"}
    response = api_client.post(reset_url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Your password has been successfully reset."
    mock_user.set_password.assert_called_once_with("NewStrongPass123!")
    mock_user.save.assert_called_once()


@patch("rbac.views.User.objects.filter")
def test_missing_fields_returns_400(mock_user_filter, api_client, reset_url):
    response = api_client.post(reset_url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "UID, token, and new_password are required" in str(response.data)


@patch("rbac.views.User.objects.filter")
def test_invalid_uid_returns_400(mock_user_filter, api_client, reset_url):
    payload = {
        "uid": "invalidbase64@@@",
        "token": "sometoken",
        "new_password": "anything",
    }
    response = api_client.post(reset_url, payload, format="json")
    assert response.status_code == 400
    assert "uid" in response.data
    assert response.data["uid"] == "Invalid value"





@patch("rbac.views.User.objects.filter")
def test_user_not_found_returns_400(mock_user_filter, api_client, reset_url):
    uid = urlsafe_base64_encode(force_bytes(999))  # valid UID format
    mock_user_filter.return_value.first.return_value = None  # simulate no user found

    payload = {"uid": uid, "token": "sometoken", "new_password": "NewPassword123!"}
    response = api_client.post(reset_url, payload, format="json")

    assert response.status_code == 400
    assert "uid" in response.data
    assert response.data["uid"] == "Invalid value"


@patch("rbac.views.default_token_generator.check_token")
@patch("rbac.views.User.objects.filter")
def test_invalid_token_returns_400(mock_user_filter, mock_check_token, api_client, reset_url, mock_user):
    uid = urlsafe_base64_encode(force_bytes(mock_user.pk))
    mock_user_filter.return_value.first.return_value = mock_user
    mock_check_token.return_value = False

    payload = {"uid": uid, "token": "invalid-token", "new_password": "NewPassword123!"}
    response = api_client.post(reset_url, payload, format="json")

    assert response.status_code == 400
    assert "detail" in response.data
    assert response.data["detail"] == "Invalid or expired token"

