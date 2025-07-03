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
from organization.models import BrandPageSliceHeadline
from unittest.mock import patch
from organization.models import BrandPageSlices
from organization.serializers import BrandPageSlicesSerializer
from organization.viewsets import BrandPageSlicesViewSet
from rest_framework.test import force_authenticate

# @pytest.fixture
# def api_factory():
#     return APIRequestFactory()

@pytest.fixture
def api_client():
    return APIClient()

# @pytest.fixture
# def mock_user():
#     user = MagicMock(spec=DirectUser)
#     user.is_authenticated = True
#     return user

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


# # -------------------- Tests for BrandPageSlices --------------------

@pytest.mark.django_db
def test_create_brand_page_slice(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Slice Create Page",
        slug="slice-create-page"
    )

    payload = {
        "brand_page": brand_page.id,
        "default_name": "Header Section",
        "description": "This is the header section of the page.",
        "slice_key": "header"
    }

    response = api_client.post("/api/brand-page-slices/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["default_name"] == "Header Section"
    assert response.data["description"] == "This is the header section of the page."
    assert response.data["slice_key"] == "header"


@pytest.mark.django_db
def test_list_brand_page_slices(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Slice List Page",
        slug="slice-list-page"
    )

    BrandPageSlices.objects.create(
        brand_page=brand_page,
        default_name="Intro Section",
        description="An introductory slice.",
        slice_key="intro"
    )

    BrandPageSlices.objects.create(
        brand_page=brand_page,
        default_name="Footer Section",
        description="The footer of the page.",
        slice_key="footer"
    )

    response = api_client.get("/api/brand-page-slices/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_retrieve_brand_page_slice(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Slice Retrieve Page",
        slug="slice-retrieve-page"
    )

    slice_obj = BrandPageSlices.objects.create(
        brand_page=brand_page,
        default_name="Main Content",
        description="Main content area.",
        slice_key="main-content"
    )

    response = api_client.get(f"/api/brand-page-slices/{slice_obj.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["default_name"] == "Main Content"
    assert response.data["slice_key"] == "main-content"


@pytest.mark.django_db
def test_update_brand_page_slice(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Slice Update Page",
        slug="slice-update-page"
    )

    slice_obj = BrandPageSlices.objects.create(
        brand_page=brand_page,
        default_name="Side Bar",
        description="A sidebar section.",
        slice_key="sidebar"
    )

    updated_data = {
        "default_name": "Updated Sidebar",
        "description": "Updated sidebar section."
    }

    response = api_client.patch(f"/api/brand-page-slices/{slice_obj.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["default_name"] == "Updated Sidebar"
    assert response.data["description"] == "Updated sidebar section."


@pytest.mark.django_db
def test_delete_brand_page_slice(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Slice Delete Page",
        slug="slice-delete-page"
    )

    slice_obj = BrandPageSlices.objects.create(
        brand_page=brand_page,
        default_name="Temporary Slice",
        description="To be deleted.",
        slice_key="temp"
    )

    response = api_client.delete(f"/api/brand-page-slices/{slice_obj.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSlices.objects.filter(id=slice_obj.id).exists()
