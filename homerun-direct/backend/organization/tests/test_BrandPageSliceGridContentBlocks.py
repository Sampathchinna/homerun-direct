

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from organization.models import BrandPageSliceGridContentBlocks, BrandPages, Organization, Brand
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


@pytest.mark.django_db
def test_create_brand_page_slice_grid_content_block(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Grid Content Block Page",
        slug="grid-content-block-page"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "custom_name": "Grid Block 1",  # Ensure it matches the name you want to test
        "column_data": {
            "column1": "Product 1",
            "column2": "Product 2"
        },
        "number_of_columns": 2
    }

    response = authenticated_client.post(
        "/api/brand-page-slice-grid-content-blocks/", payload, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["custom_name"] == "Grid Block 1"
    assert response.data["column_data"]["column1"] == "Product 1"
    assert response.data["number_of_columns"] == 2


@pytest.mark.django_db
def test_retrieve_brand_page_slice_grid_content_block(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Grid Content Block",
        slug="retrieve-grid-content-block"
    )

    # Create the grid content block with the same custom_name as the one created above
    grid_content_block = BrandPageSliceGridContentBlocks.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Grid Block 1",  # Match the custom_name
        column_data={"column1": "Product 1"},
        number_of_columns=1
    )

    response = authenticated_client.get(
        f"/api/brand-page-slice-grid-content-blocks/{grid_content_block.id}/"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Grid Block 1"


@pytest.mark.django_db
def test_list_brand_page_slice_grid_content_blocks(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="List Grid Content Blocks",
        slug="list-grid-content-blocks"
    )

    BrandPageSliceGridContentBlocks.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Grid Block A",
        column_data={"column1": "Item A"},
        number_of_columns=1
    )
    BrandPageSliceGridContentBlocks.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Grid Block B",
        column_data={"column2": "Item B"},
        number_of_columns=2
    )

    response = authenticated_client.get("/api/brand-page-slice-grid-content-blocks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_update_brand_page_slice_grid_content_block(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Grid Content Block",
        slug="update-grid-content-block"
    )

    grid_content_block = BrandPageSliceGridContentBlocks.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Old Grid Block",
        column_data={"column1": "Old Product"},
        number_of_columns=1
    )

    updated_data = {
        "custom_name": "Updated Grid Block",
        "column_data": {"column1": "New Product"},
        "number_of_columns": 2
    }

    response = authenticated_client.patch(
        f"/api/brand-page-slice-grid-content-blocks/{grid_content_block.id}/", updated_data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Updated Grid Block"
    assert response.data["column_data"]["column1"] == "New Product"
    assert response.data["number_of_columns"] == 2


@pytest.mark.django_db
def test_delete_brand_page_slice_grid_content_block(authenticated_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Grid Content Block",
        slug="delete-grid-content-block"
    )

    grid_content_block = BrandPageSliceGridContentBlocks.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Delete Me",
        column_data={"column1": "To Delete"},
        number_of_columns=1
    )

    response = authenticated_client.delete(
        f"/api/brand-page-slice-grid-content-blocks/{grid_content_block.id}/"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSliceGridContentBlocks.objects.filter(id=grid_content_block.id).exists()
