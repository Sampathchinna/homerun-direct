import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APIClient
from unittest.mock import patch


@pytest.mark.django_db
def test_password_reset_success(settings):
    client = APIClient()
    User = get_user_model()

    user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")

    with patch.object(User, "email_user") as mock_email_user:
        settings.FRONTEND_URL = "http://frontend.com"

        url = reverse("password_reset")
        data = {"email": "test@example.com"}
        response = client.post(url, data)

        assert response.status_code == 200
        assert response.data["data"]["email"] == "test@example.com"

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        expected_link = f"http://frontend.com/reset-password/{uid}/{token}"
        assert response.data["data"]["reset_link"] == expected_link
        mock_email_user.assert_called_once()


@pytest.mark.django_db
def test_password_reset_email_not_found():
    client = APIClient()
    url = reverse("password_reset")
    data = {"email": "notfound@example.com"}
    response = client.post(url, data)

    assert response.status_code == 400
    assert "email" in response.data
    assert response.data["email"][0] == "No user found with this email address."


@pytest.mark.django_db
def test_password_reset_missing_email_field():
    client = APIClient()
    url = reverse("password_reset")
    data = {}  # No email
    response = client.post(url, data)

    assert response.status_code == 400
    assert "email" in response.data
    assert "This field is required." in response.data["email"][0]


@pytest.mark.django_db
def test_password_reset_invalid_email_format():
    client = APIClient()
    url = reverse("password_reset")
    data = {"email": "notanemail"}  # Invalid format
    response = client.post(url, data)

    assert response.status_code == 400
    assert "email" in response.data
    assert "Enter a valid email address." in response.data["email"][0]




# import pytest
# from unittest.mock import patch, MagicMock
# from django.urls import reverse
# from rest_framework.test import APIClient
# from rest_framework import status
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.conf import settings


# @pytest.fixture
# def api_client():
#     return APIClient()


# @pytest.fixture
# def mock_user():
#     mock_user = MagicMock()
#     mock_user.pk = 1
#     mock_user.email = "test@example.com"
#     mock_user.username = "testuser"
#     mock_user.email_user = MagicMock()
#     return mock_user


# @patch("rbac.serializers.User.objects.filter")
# @patch("rbac.serializers.User.objects.get")
# def test_password_reset_success(mock_get_user, mock_filter_user, api_client, mock_user, settings):
#     """
#     Test successful password reset request with a valid email.
#     """
#     settings.FRONTEND_URL = "http://frontend.com"

#     mock_filter_user.return_value.exists.return_value = True
#     mock_get_user.return_value = mock_user

#     url = reverse("password_reset")
#     data = {"email": "test@example.com"}

#     response = api_client.post(url, data)

#     # Assert response
#     assert response.status_code == status.HTTP_200_OK
#     assert "reset_link" in response.data["data"]
#     assert data["email"] == response.data["data"]["email"]

#     # Check if token generated correctly
#     uid = urlsafe_base64_encode(force_bytes(mock_user.pk))
#     token = default_token_generator.make_token(mock_user)
#     expected_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
#     assert expected_link == response.data["data"]["reset_link"]

#     # Ensure email was sent
#     mock_user.email_user.assert_called_once()


# @patch("rbac.serializers.User.objects.filter")
# def test_password_reset_invalid_email(mock_filter_user, api_client):
#     """
#     Test password reset with a non-existent email.
#     """
#     mock_filter_user.return_value.exists.return_value = False

#     url = reverse("password_reset")
#     data = {"email": "nonexistent@example.com"}

#     response = api_client.post(url, data)

#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "email" in response.data
#     assert response.data["email"][0] == "No user found with this email address."


# def test_password_reset_missing_email_field(api_client):
#     """
#     Test missing email field in the request payload.
#     """
#     url = reverse("password_reset")
#     data = {}

#     response = api_client.post(url, data)

#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "email" in response.data


# def test_password_reset_invalid_email_format(api_client):
#     """
#     Test invalid email format.
#     """
#     url = reverse("password_reset")
#     data = {"email": "invalid-email-format"}

#     response = api_client.post(url, data)

#     # Depending on how EmailField handles this
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "email" in response.data
