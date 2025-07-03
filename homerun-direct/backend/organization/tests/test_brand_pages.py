import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient
from rest_framework import status
from django.test.utils import override_settings
from django.http import Http404
from organization.models import Brand, Organization
from master.models import Language, Currency, OrganizationType, CompanyType, PaymentProcessor, Location, SubscriptionPlan
from rbac.models import DirectUser
from organization.models import BrandPages  # Assuming it’s in brand.models
from organization.viewsets import BrandPagesViewSet  # Adjust according to actual module
from unittest.mock import patch






@pytest.fixture
def api_factory():
    return APIRequestFactory()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def mock_user():
    user = MagicMock(spec=DirectUser)
    user.is_authenticated = True
    return user

@pytest.fixture
def brand():
    user = DirectUser.objects.create(username="testuser")
    language = Language.objects.create(old_id="1", value="en")
    currency = Currency.objects.create(old_id="1", value="usd")
    org_type = OrganizationType.objects.create(old_id="1", value="hotel")
    company_type = CompanyType.objects.create(old_id="1", value="llc")
    processor = PaymentProcessor.objects.create(label="Stripe", value="stripe")
    location = Location.objects.create(
        apt_suite="101", city="TestCity", state_province="TS",
        postal_code="12345", country="TestLand", street_address="123 Test St",
        latitude=12.345678, longitude=98.765432, exact=True,
        timezone="UTC", locationable_type_id=1
    )
    plan = SubscriptionPlan.objects.create(
        provider=processor, name="Pro Plan", interval="monthly", price_cents=1000
    )
    org = Organization.objects.create(
        organization_name="Test Org", user=user, language=language,
        currency=currency, organization_type=org_type,
        company_type=company_type, payment_processor=processor,
        location=location, subscription_plan=plan, terms_agreement=True,
    )
    return Brand.objects.create(organization=org, name="Brand1", currency="usd", language="en")

@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
@patch("organization.viewsets.BrandPagesViewSet.get_queryset")
def test_list_brandpages(mock_get_queryset, api_factory, mock_user):
    mock_instance = MagicMock()
    mock_instance.configure_mock(title="Test Page", slug="test-page")
    mock_get_queryset.return_value = [mock_instance]

    view = BrandPagesViewSet.as_view({"get": "list"})
    request = api_factory.get("/api/brand-pages/")
    force_authenticate(request, user=mock_user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_create_brandpage(api_client, brand):
    payload = {
        "brand": brand.id,
        "title": "New Page",
        "slug": "new-page",
        "template": 1,
        "description": "This is a test page",
        "payload": {"content": "Sample"},
        "featured": True,
        "published": True
    }

    response = api_client.post("/api/brand-pages/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "New Page"


@pytest.mark.django_db
def test_update_brandpage(api_client, brand):
    brandpage = BrandPages.objects.create(
        brand=brand,
        title="Old Title",
        slug="old-title"
    )

    updated_data = {
        "title": "Updated Title",
        "slug": "updated-title"
    }

    response = api_client.patch(f"/api/brand-pages/{brandpage.pk}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Updated Title"

@pytest.mark.django_db
def test_delete_brandpage(api_client, brand):
    brandpage = BrandPages.objects.create(
        brand=brand,
        title="To Delete",
        slug="to-delete"
    )

    response = api_client.delete(f"/api/brand-pages/{brandpage.pk}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT

@patch("organization.viewsets.BrandPagesViewSet.get_object")
def test_retrieve_brandpage_not_found(mock_get_object, api_factory, mock_user):
    mock_get_object.side_effect = Http404("Not Found")
    view = BrandPagesViewSet.as_view({"get": "retrieve"})
    request = api_factory.get("/api/brand-pages/999/")
    force_authenticate(request, user=mock_user)
    response = view(request, pk=999)

    assert response.status_code == status.HTTP_404_NOT_FOUND




@pytest.mark.django_db
@patch("organization.viewsets.BrandPagesViewSet.get_object")
def test_retrieve_brandpage(mock_get_object, api_factory, mock_user, brand):
    # Create a real BrandPages object linked to Brand from fixture
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Test Page",
        slug="test-page"
    )

    # Mock get_object to return the real instance
    mock_get_object.return_value = brand_page

    view = BrandPagesViewSet.as_view({"get": "retrieve"})
    request = api_factory.get(f"/api/brand-pages/{brand_page.id}/")
    force_authenticate(request, user=mock_user)
    response = view(request, pk=brand_page.id)

    assert response.status_code == 200
    assert response.data["title"] == "Test Page"


