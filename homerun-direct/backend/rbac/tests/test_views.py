import pytest
from unittest import mock
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from rbac.serializers import GoogleAuthSerializer, CustomPasswordResetSerializer
from django.conf import settings
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestCustomLoginView:
    def test_successful_login(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="test", password="testpass")
        response = client.post("/auth/login/", {"username": "test", "password": "testpass"})
        assert response.status_code == 200
        assert "access_token" in response.data

    def test_invalid_login(self, client):
        response = client.post("/auth/login/", {"username": "invalid", "password": "wrong"})
        assert response.status_code == 400
        assert response.data["detail"] == "Invalid username or password"

    @patch("rbac.views.requests.post")
    def test_legacy_user_creation_success(self, mock_post, client, django_user_model, settings):
        mock_post.return_value.status_code = 200
        settings.CURRENT_DIRECT_LOGIN_URL = "https://dummy-login.com"
        response = client.post("/auth/login/", {"username": "legacy@domain.com", "password": "pass123"})
        assert response.status_code == 200
        assert "access_token" in response.data

    @patch("rbac.views.requests.post")
    def test_legacy_service_unavailable(self, mock_post, client, settings):
        settings.CURRENT_DIRECT_LOGIN_URL = "https://dummy-login.com"
        mock_post.side_effect = requests.RequestException
        response = client.post("/auth/login/", {"username": "legacy@domain.com", "password": "pass123"})
        assert response.status_code == 503
        assert "Legacy authentication service unavailable." in response.data["detail"]


@pytest.mark.django_db
class TestCustomPasswordResetView:
    @patch("rbac.views.CustomPasswordResetSerializer.save")
    def test_password_reset_success(self, mock_save, client, django_user_model):
        mock_save.return_value = {"reset_link": "http://reset-link"}
        django_user_model.objects.create_user(username="resetuser", email="user@example.com", password="testpass")
        response = client.post("/auth/forgot-password/", {"email": "user@example.com"})
        assert response.status_code == 200
        assert "reset_link" in response.data["data"]



@pytest.mark.django_db
class TestCustomPasswordResetConfirmView:
    def test_missing_fields(self, client):
        response = client.post("/auth/reset-password/", {})
        assert response.status_code == 400
        assert "fields" in response.data
        assert response.data["fields"] == "UID, token, and new_password are required"



    def test_invalid_uid(self, client):
        response = client.post("/auth/reset-password/", {"uid": "invalid", "token": "abc", "new_password": "123456"})
        assert response.status_code == 400
        assert "uid" in response.data or "non_field_errors" in response.data

    def test_invalid_token(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="testuser", email="t@t.com", password="pass")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        response = client.post("/auth/reset-password/", {
            "uid": uid,
            "token": "invalid",
            "new_password": "newpass"
        })
        assert response.status_code == 400
        assert "detail" in response.data
        assert response.data["detail"] == "Invalid or expired token"



    def test_successful_password_reset(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="testuser", email="t@t.com", password="pass")
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        response = client.post("/auth/reset-password/", {"uid": uid, "token": token, "new_password": "newpass123"})
        assert response.status_code == 200
        assert response.data["message"] == "Your password has been successfully reset."


