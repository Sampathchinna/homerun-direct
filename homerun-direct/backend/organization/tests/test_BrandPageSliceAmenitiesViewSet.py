import pytest
from rest_framework import status
from rest_framework.test import APIClient

from organization.models import BrandPageSliceAmenities, BrandPages, Organization, Brand
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
def test_create_brand_page_slice_amenity(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Amenities Page",
        slug="amenities-page"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "custom_name": "Swimming Pool",
        "amenities_data": {
            "amenity1": "Swimming Pool",
            "amenity2": "Gym"
        }
    }

    response = authenticated_client.post(
        "/api/brand-page-slice-amenities/", payload, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["custom_name"] == "Swimming Pool"
    assert response.data["amenities_data"]["amenity1"] == "Swimming Pool"


@pytest.mark.django_db
def test_retrieve_brand_page_slice_amenity(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Amenities",
        slug="retrieve-amenities"
    )

    # Create the amenity with the same custom_name as the one created above
    amenity = BrandPageSliceAmenities.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Swimming Pool",  # Match the custom_name
        amenities_data={"amenity": "Outdoor Pool"}
    )

    response = authenticated_client.get(
        f"/api/brand-page-slice-amenities/{amenity.id}/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Swimming Pool"


@pytest.mark.django_db
def test_list_brand_page_slice_amenities(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="List Amenities",
        slug="list-amenities"
    )

    BrandPageSliceAmenities.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Swimming Pool",
        amenities_data={"amenity": "Ocean View Pool"}
    )
    BrandPageSliceAmenities.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Gym",
        amenities_data={"amenity": "Fitness Center"}
    )

    response = authenticated_client.get("/api/brand-page-slice-amenities/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_update_brand_page_slice_amenity(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Amenities",
        slug="update-amenities"
    )

    amenity = BrandPageSliceAmenities.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Old Amenity",
        amenities_data={"amenity": "Old Pool"}
    )

    updated_data = {
        "custom_name": "Updated Amenity",
        "amenities_data": {"amenity": "New Pool"}
    }

    response = authenticated_client.patch(
        f"/api/brand-page-slice-amenities/{amenity.id}/", updated_data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Updated Amenity"
    assert response.data["amenities_data"]["amenity"] == "New Pool"

@pytest.mark.django_db
def test_delete_brand_page_slice_amenity(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Amenity",
        slug="delete-amenity"
    )

    amenity = BrandPageSliceAmenities.objects.create(
        brand_page=brand_page,
        page_sort=3,
        custom_name="Delete Me",
        amenities_data={"amenity": "To Delete"}
    )

    response = authenticated_client.delete(
        f"/api/brand-page-slice-amenities/{amenity.id}/"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSliceAmenities.objects.filter(id=amenity.id).exists()
