# backend/organization/tests/test_brand_page_slice_featured_listings.py

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from organization.models import BrandPageSliceFeaturedListings, BrandPages, Organization, Brand
from rbac.models import DirectUser
from master.models import (
    Language, Currency, OrganizationType, CompanyType,
    PaymentProcessor, Location, SubscriptionPlan
)

# ----------- Fixtures -------------------

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return DirectUser.objects.create(username="testuser")

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def brand(user):
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
    organization = Organization.objects.create(
        organization_name="Test Org", user=user, language=language,
        currency=currency, organization_type=org_type,
        company_type=company_type, payment_processor=processor,
        location=location, subscription_plan=plan, terms_agreement=True,
    )
    return Brand.objects.create(
        organization=organization, name="Brand1", currency="usd", language="en"
    )

# ----------- Tests -----------------------

@pytest.mark.django_db
def test_create_brand_page_slice_featured_listing(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Featured Listings Page",
        slug="featured-listings-page"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "custom_name": "Cozy Cottage",  # Make sure this matches the name you want to test
        "listings_data": {
            "listing1": "Villa Ocean View",
            "listing2": "Mountain Cabin"
        }
    }

    response = authenticated_client.post(
        "/api/brand-page-slice-featured-listings/", payload, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["custom_name"] == "Cozy Cottage"
    assert response.data["listings_data"]["listing1"] == "Villa Ocean View"


@pytest.mark.django_db
def test_retrieve_brand_page_slice_featured_listing(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Featured Listing",
        slug="retrieve-featured-listing"
    )

    # Create the listing with the same custom_name as the one created above
    listing = BrandPageSliceFeaturedListings.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Cozy Cottage",  # Match the custom_name
        listings_data={"listing": "Small Cottage"}
    )

    response = authenticated_client.get(
        f"/api/brand-page-slice-featured-listings/{listing.id}/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Cozy Cottage"


@pytest.mark.django_db
def test_list_brand_page_slice_featured_listings(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="List Featured Listings",
        slug="list-featured-listings"
    )

    BrandPageSliceFeaturedListings.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Listing A",
        listings_data={"listing": "Ocean Side"}
    )
    BrandPageSliceFeaturedListings.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Listing B",
        listings_data={"listing": "City Apartment"}
    )

    response = authenticated_client.get("/api/brand-page-slice-featured-listings/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_update_brand_page_slice_featured_listing(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Featured Listing",
        slug="update-featured-listing"
    )

    listing = BrandPageSliceFeaturedListings.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Old Listing",
        listings_data={"listing": "Old Place"}
    )

    updated_data = {
        "custom_name": "Updated Listing",
        "listings_data": {"listing": "New Place"}
    }

    response = authenticated_client.patch(
        f"/api/brand-page-slice-featured-listings/{listing.id}/", updated_data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Updated Listing"
    assert response.data["listings_data"]["listing"] == "New Place"

@pytest.mark.django_db
def test_delete_brand_page_slice_featured_listing(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Featured Listing",
        slug="delete-featured-listing"
    )

    listing = BrandPageSliceFeaturedListings.objects.create(
        brand_page=brand_page,
        page_sort=3,
        custom_name="Delete Me",
        listings_data={"listing": "To Delete"}
    )

    response = authenticated_client.delete(
        f"/api/brand-page-slice-featured-listings/{listing.id}/"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSliceFeaturedListings.objects.filter(id=listing.id).exists()


