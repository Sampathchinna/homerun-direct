import pytest
from rest_framework.test import APIClient
from rest_framework import status
from organization.models import Brand, Organization
from master.models import Language, Currency, OrganizationType, CompanyType, PaymentProcessor, Location, SubscriptionPlan
from rbac.models import DirectUser
from organization.models import BrandPages  # Assuming it’s in brand.models
from organization.models import BrandPageSliceHeadline


@pytest.fixture
def api_client():
    return APIClient()



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
def test_create_brand_page_slice_headline(api_client, brand):
    # First create a BrandPage instance
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Headline Page",
        slug="headline-page"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "headline_text": "Welcome to our headline"
    }

    response = api_client.post("/api/brand-page-slice-headers/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["headline_text"] == "Welcome to our headline"


@pytest.mark.django_db
def test_list_brand_page_slice_headlines(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="List Headline",
        slug="list-headline"
    )

    BrandPageSliceHeadline.objects.create(
        brand_page=brand_page,
        page_sort=1,
        headline_text="Headline 1"
    )
    BrandPageSliceHeadline.objects.create(
        brand_page=brand_page,
        page_sort=2,
        headline_text="Headline 2"
    )

    response = api_client.get("/api/brand-page-slice-headers/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_retrieve_brand_page_slice_headline(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Headline",
        slug="retrieve-headline"
    )

    headline = BrandPageSliceHeadline.objects.create(
        brand_page=brand_page,
        page_sort=3,
        headline_text="Specific Headline"
    )

    response = api_client.get(f"/api/brand-page-slice-headers/{headline.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["headline_text"] == "Specific Headline"


@pytest.mark.django_db
def test_update_brand_page_slice_headline(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Headline",
        slug="update-headline"
    )

    headline = BrandPageSliceHeadline.objects.create(
        brand_page=brand_page,
        page_sort=5,
        headline_text="Old Headline"
    )

    updated_data = {
        "headline_text": "Updated Headline"
    }

    response = api_client.patch(f"/api/brand-page-slice-headers/{headline.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["headline_text"] == "Updated Headline"


@pytest.mark.django_db
def test_delete_brand_page_slice_headline(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Headline",
        slug="delete-headline"
    )

    headline = BrandPageSliceHeadline.objects.create(
        brand_page=brand_page,
        page_sort=10,
        headline_text="Delete Me"
    )

    response = api_client.delete(f"/api/brand-page-slice-headers/{headline.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSliceHeadline.objects.filter(id=headline.id).exists()
