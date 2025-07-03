
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
from organization.models import BrandPageSlicePullQuotes
from organization.serializers import BrandPageSlicePullQuotesSerializer
from organization.viewsets import BrandPageSlicePullQuotesViewSet
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






@pytest.mark.django_db
def test_create_brand_page_slice_pull_quote(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Quote Page",
        slug="quote-page"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "custom_name": "Quote Block 1",
        "quote_text": "Believe in yourself.",
        "quote_author": "John Doe",
        "quote_author_image": "https://example.com/author.jpg"
    }

    response = api_client.post("/api/brand-page-slice-pull-quotes/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["quote_text"] == "Believe in yourself."
    assert "John Doe" in response.data["quote_author"]

@pytest.mark.django_db
def test_list_brand_page_slice_pull_quotes(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Quote List Page",
        slug="quote-list"
    )

    BrandPageSlicePullQuotes.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Quote A",
        quote_text="Stay hungry.",
        quote_author="Steve",
        quote_author_image="https://example.com/steve.jpg"
    )

    BrandPageSlicePullQuotes.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Quote B",
        quote_text="Stay foolish.",
        quote_author="Woz",
        quote_author_image="https://example.com/woz.jpg"
    )

    response = api_client.get("/api/brand-page-slice-pull-quotes/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2

@pytest.mark.django_db
def test_retrieve_brand_page_slice_pull_quote(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Quote Page",
        slug="retrieve-quote"
    )

    quote = BrandPageSlicePullQuotes.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Retrieve Quote",
        quote_text="Push the limits.",
        quote_author="Elon",
        quote_author_image="https://example.com/elon.jpg"
    )

    response = api_client.get(f"/api/brand-page-slice-pull-quotes/{quote.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["quote_text"] == "Push the limits."

@pytest.mark.django_db
def test_update_brand_page_slice_pull_quote(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Quote Page",
        slug="update-quote"
    )

    quote = BrandPageSlicePullQuotes.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Old Quote",
        quote_text="Original text.",
        quote_author="Old Author",
        quote_author_image="https://example.com/old.jpg"
    )

    updated_data = {
        "quote_text": "Updated text.",
        "quote_author": "New Author",
        "quote_author_image": "https://example.com/new.jpg"
    }

    response = api_client.patch(f"/api/brand-page-slice-pull-quotes/{quote.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["quote_text"] == "Updated text."
    assert "New Author" in response.data["quote_author"]

@pytest.mark.django_db
def test_delete_brand_page_slice_pull_quote(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Quote Page",
        slug="delete-quote"
    )

    quote = BrandPageSlicePullQuotes.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Delete Quote",
        quote_text="To be deleted.",
        quote_author="Someone",
        quote_author_image="https://example.com/delete.jpg"
    )

    response = api_client.delete(f"/api/brand-page-slice-pull-quotes/{quote.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSlicePullQuotes.objects.filter(id=quote.id).exists()
