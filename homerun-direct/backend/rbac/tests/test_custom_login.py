import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def login_url():
    return reverse("custom-login")

@pytest.mark.django_db
@patch("rbac.views.authenticate")
@patch("rbac.views.store_user_entities_in_session")
def test_successful_login_existing_user(mock_store_session, mock_authenticate, api_client, login_url):
    mock_user = MagicMock()
    mock_user.is_authenticated = True
    mock_user.is_superuser = False
    mock_user.username = "testuser"
    mock_user.id = 1
    mock_user.phone_number = "1234567890"
    mock_authenticate.return_value = mock_user

    payload = {"username": "testuser", "password": "testpass"}
    response = api_client.post(login_url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.data
    assert response.data["username"] == "testuser"
    mock_store_session.assert_called_once_with(mock_user, response.wsgi_request.session)

@pytest.mark.django_db
@patch("rbac.views.requests.post")
@patch("rbac.views.authenticate")
@patch("rbac.views.store_user_entities_in_session")
@patch("rbac.views.User.objects.create_user")
@patch("rbac.views.User.objects.filter")
def test_successful_legacy_login(
    mock_user_filter,
    mock_create_user,
    mock_store_session,
    mock_authenticate,
    mock_requests_post,
    api_client,
    login_url
):
    """
    Test successful login via legacy authentication service.
    """
    # Ensure that the user is not found in the local DB
    mock_user_filter.return_value.exists.return_value = False

    # Mock legacy authentication response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "email": "legacyuser@example.com",
        "full_name": "Legacy User",
        "username": "legacyuser",
        "phone_number": "1234567890"
    }
    mock_requests_post.return_value = mock_response

    # Mock the user creation (this happens after legacy auth)
    legacy_user = MagicMock(spec=User)
    legacy_user.id = 100
    legacy_user.username = "legacyuser"
    legacy_user.phone_number = "1234567890"
    legacy_user.is_authenticated = True
    legacy_user.is_superuser = False  # Ensure this is not a superuser
    mock_create_user.return_value = legacy_user

    # Mock authenticate to return the legacy user after they are created
    mock_authenticate.side_effect = [None, legacy_user]  # First None for not found, then legacy user

    # Payload for the legacy login request
    payload = {"username": "legacyuser@example.com", "password": "legacy123"}
    response = api_client.post(login_url, payload, format="json")

    # Verify store_user_entities_in_session is called
    mock_store_session.assert_called_once_with(legacy_user, response.wsgi_request.session)

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.data
    assert response.data["username"] == "legacyuser"
    assert response.data["userId"] == legacy_user.id
    assert response.data["phone_number"] == legacy_user.phone_number




@patch("rbac.views.authenticate")
@patch("rbac.views.User.objects.filter")
def test_invalid_credentials(mock_user_filter, mock_authenticate, api_client, login_url):
    mock_authenticate.return_value = None
    mock_user_filter.return_value.exists.return_value = True

    payload = {"username": "wronguser", "password": "wrongpass"}
    response = api_client.post(login_url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Invalid username or password"

from requests.exceptions import RequestException

@pytest.mark.django_db
@patch("rbac.views.requests.post")
@patch("rbac.views.authenticate")
@patch("rbac.views.User.objects.filter")
def test_legacy_auth_service_failure(mock_user_filter, mock_authenticate, mock_requests_post, api_client, login_url):
    """
    Test that a failure in the legacy auth service results in a 503 response.
    """
    mock_authenticate.return_value = None
    mock_user_filter.return_value.exists.return_value = False

    # Simulating a failure of the legacy authentication service
    mock_requests_post.side_effect = RequestException("Service unavailable")

    payload = {"username": "legacyuser@example.com", "password": "legacy123"}
    response = api_client.post(login_url, payload, format="json")

    # Assert service failure response
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.data["detail"] == "Legacy authentication service unavailable."




# import pytest
# from unittest.mock import patch, MagicMock
# from django.urls import reverse
# from rest_framework.test import APIClient
# from rest_framework import status
# from django.contrib.auth import get_user_model

# User = get_user_model()

# @pytest.fixture
# def api_client():
#     return APIClient()

# @pytest.fixture
# def login_url():
#     return reverse("custom-login")

# @pytest.mark.django_db
# @patch("rbac.views.authenticate")
# @patch("rbac.views.store_user_entities_in_session")
# def test_successful_login_existing_user(mock_store_session, mock_authenticate, api_client, login_url):
#     mock_user = MagicMock()
#     mock_user.is_authenticated = True
#     mock_user.is_superuser = False
#     mock_user.username = "testuser"
#     mock_user.id = 1
#     mock_user.phone_number = "1234567890"
#     mock_authenticate.return_value = mock_user

#     payload = {"username": "testuser", "password": "testpass"}
#     response = api_client.post(login_url, payload, format="json")

#     assert response.status_code == status.HTTP_200_OK
#     assert "access_token" in response.data
#     assert response.data["username"] == "testuser"
#     mock_store_session.assert_called_once_with(mock_user, response.wsgi_request.session)

# @pytest.mark.django_db
# @patch("rbac.views.requests.post")
# @patch("rbac.views.authenticate")
# @patch("rbac.views.store_user_entities_in_session")
# @patch("rbac.views.User.objects.create_user")
# @patch("rbac.views.User.objects.filter")
# def test_successful_legacy_login(
#     mock_user_filter,
#     mock_create_user,
#     mock_store_session,
#     mock_authenticate,
#     mock_requests_post,
#     api_client,
#     login_url
# ):
#     """
#     Test successful login via legacy authentication service.
#     """
#     mock_authenticate.return_value = None
#     mock_user_filter.return_value.exists.return_value = False

#     mock_response = MagicMock()
#     mock_response.status_code = 200
#     mock_response.json.return_value = {
#         "email": "legacyuser@example.com",
#         "full_name": "Legacy User",
#         "username": "legacyuser",
#         "phone_number": "1234567890"
#     }
#     mock_requests_post.return_value = mock_response

#     legacy_user = MagicMock()
#     legacy_user.id = 100  # important: must be an integer
#     legacy_user.username = "legacyuser"
#     legacy_user.phone_number = "1234567890"
#     legacy_user.is_authenticated = True
#     mock_create_user.return_value = legacy_user

#     payload = {"username": "legacyuser@example.com", "password": "legacy123"}
#     response = api_client.post(login_url, payload, format="json")

#     assert response.status_code == status.HTTP_200_OK
#     assert "access_token" in response.data
#     assert response.data["username"] == "legacyuser"
#     mock_store_session.assert_called_once()


# @patch("rbac.views.authenticate")
# @patch("rbac.views.User.objects.filter")
# def test_invalid_credentials(mock_user_filter, mock_authenticate, api_client, login_url):
#     mock_authenticate.return_value = None
#     mock_user_filter.return_value.exists.return_value = True

#     payload = {"username": "wronguser", "password": "wrongpass"}
#     response = api_client.post(login_url, payload, format="json")

#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.data["detail"] == "Invalid username or password"

# @pytest.mark.django_db
# @patch("rbac.views.requests.post")
# @patch("rbac.views.authenticate")
# @patch("rbac.views.User.objects.filter")
# def test_legacy_auth_service_failure(mock_user_filter, mock_authenticate, mock_requests_post, api_client, login_url):
#     """
#     Test that a failure in the legacy auth service results in a 503 response.
#     """
#     mock_authenticate.return_value = None
#     mock_user_filter.return_value.exists.return_value = False
#     mock_requests_post.side_effect = Exception("Service unavailable")

#     payload = {"username": "legacyuser@example.com", "password": "legacy123"}
#     response = api_client.post(login_url, payload, format="json")

#     assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
#     assert response.data["detail"] == "Legacy authentication service unavailable."
