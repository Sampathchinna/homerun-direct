import stripe
from unittest.mock import patch, MagicMock
from rest_framework.test import force_authenticate
import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from organization.viewsets import OrganizationViewSet
from rest_framework import status
from rest_framework.request import Request

User = get_user_model()

@pytest.fixture
def api_factory():
    return APIRequestFactory()

@pytest.fixture
def test_user():
    return User(id=1, email='test@example.com')



from rest_framework.request import Request
from django.http import HttpRequest

@pytest.fixture
def mock_request_with_session(api_factory, test_user):
    request = api_factory.get("/api/organization/")
    request.session = {}  # Mock session
    force_authenticate(request, user=test_user)
    return request


# ✅ POSITIVE: List view (Elasticsearch success)
@patch("organization.viewsets.OrganizationViewSet.search_elasticsearch")
def test_list_success(mock_search, api_factory, test_user):
    mock_search.return_value = [{"organization_name": "Org A"}]
    view = OrganizationViewSet.as_view({"get": "list"})
    request = api_factory.get("/api/organization/?page=1&per_page=1")
    request.session = {}
    force_authenticate(request, user=test_user)
    response = view(request)
    assert response.status_code == 200
    assert "response" in response.data





@patch("organization.viewsets.es.get")  # Correct path to patch
@patch("django.shortcuts.get_object_or_404")
def test_retrieve_success(mock_get_object_or_404, mock_es_get, api_factory, test_user):
    # Mock Elasticsearch response
    mock_es_get.return_value = {"_source": {"organization_name": "Test Org"}}

    # Mock fallback
    mock_org = MagicMock()
    mock_org.id = 1
    mock_org.organization_name = "Test Org"
    mock_get_object_or_404.return_value = mock_org

    # Setup view and request
    view = OrganizationViewSet.as_view({"get": "retrieve"})
    request = api_factory.get("/api/organization/1/")
    force_authenticate(request, user=test_user)

    # Call the view
    response = view(request, pk=1)

    assert response.status_code == 200
    assert response.data["organization_name"] == "Test Org"




# ✅ POSITIVE: create_checkout_session success
@patch("organization.viewsets.create_checkout_session")
@patch("organization.viewsets.RefreshToken.for_user")
def test_create_checkout_session_success(mock_refresh, mock_create, api_factory, test_user):
    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/success"
    mock_session.id = "session_123"
    mock_create.return_value = mock_session
    mock_refresh.return_value = MagicMock(access_token="access123", __str__=lambda x: "refresh123")

    view = OrganizationViewSet.as_view({"post": "create_checkout_session"})
    request = api_factory.post("/api/organization/create-checkout-session", {
        "subscription_plan_id": 1,
        "organization_id": 1
    }, format='json')
    force_authenticate(request, user=test_user)
    response = view(request)
    assert response.status_code == 201
    assert "session_url" in response.data

# ❌ NEGATIVE: create_checkout_session missing fields
def test_create_checkout_session_missing_fields(api_factory, test_user):
    view = OrganizationViewSet.as_view({"post": "create_checkout_session"})
    request = api_factory.post("/api/organization/create-checkout-session", {}, format='json')
    force_authenticate(request, user=test_user)
    response = view(request)
    assert response.status_code == 400
    assert "Required fields missing" in response.data["error"]

# ❌ NEGATIVE: create_checkout_session throws exception
@patch("organization.viewsets.create_checkout_session", side_effect=Exception("Stripe error"))
def test_create_checkout_session_exception(mock_create, api_factory, test_user):
    view = OrganizationViewSet.as_view({"post": "create_checkout_session"})
    request = api_factory.post("/api/organization/create-checkout-session", {
        "subscription_plan_id": 1,
        "organization_id": 1
    }, format='json')
    force_authenticate(request, user=test_user)
    response = view(request)
    assert response.status_code == 400
    assert "Stripe error" in response.data["error"]

# ✅ POSITIVE: verify_payment success
@patch("organization.viewsets.stripe.checkout.Session.retrieve")
@patch("organization.viewsets.get_object_or_404")
def test_verify_payment_success(mock_get_org, mock_retrieve, api_factory, test_user):
    mock_session = MagicMock()
    mock_session.payment_status = "paid"
    mock_retrieve.return_value = mock_session

    mock_org = MagicMock()
    mock_org.id = 99
    mock_get_org.return_value = mock_org

    view = OrganizationViewSet.as_view({"get": "verify_payment"})
    request = api_factory.get("/api/organization/verify-payment?session_id=session_abc")
    force_authenticate(request, user=test_user)
    response = view(request)
    assert response.status_code == 200
    assert response.data["success"]

# ❌ NEGATIVE: verify_payment without session_id
def test_verify_payment_missing_param(api_factory, test_user):
    view = OrganizationViewSet.as_view({"get": "verify_payment"})
    request = api_factory.get("/api/organization/verify-payment")
    force_authenticate(request, user=test_user)
    response = view(request)
    assert response.status_code == 400
    assert "Session ID is required." in response.data["error"]



@patch("organization.viewsets.stripe.checkout.Session.retrieve", side_effect=stripe.error.StripeError("Stripe API error"))
def test_verify_payment_stripe_error(mock_retrieve, api_factory, test_user):
    view = OrganizationViewSet.as_view({"get": "verify_payment"})
    request = api_factory.get("/api/organization/verify-payment?session_id=session_abc")
    force_authenticate(request, user=test_user)
    response = view(request)
    assert response.status_code == 400
    assert "Stripe API error" in response.data["error"]




@patch("core.mixin_es.es.get", side_effect=Exception("Document not found"))
def test_retrieve_fail(mock_es_get, api_factory, test_user):
    view = OrganizationViewSet.as_view({"get": "retrieve"})
    request = api_factory.get("/api/organization/1/")
    force_authenticate(request, user=test_user)

    response = view(request, pk=1)

    assert response.status_code == 404
    assert response.data == {"detail": "Not found."}

