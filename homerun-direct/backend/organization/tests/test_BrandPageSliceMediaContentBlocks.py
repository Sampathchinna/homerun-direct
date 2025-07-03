
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
from organization.models import BrandPageSliceMediaContentBlocks
from organization.viewsets import BrandPageSliceMediaContentBlocksViewSet
from organization.serializers import BrandPageSliceMediaContentBlocksSerializer
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
def test_create_brand_page_slice_media_content_block(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Media Content Page",
        slug="media-content"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "custom_name": "Media Block 1",
        "bg_image": "https://example.com/bg1.jpg",
        "bg_image_gallery": ["https://example.com/gallery1.jpg", "https://example.com/gallery2.jpg"],
        "bg_video": "https://example.com/video1.mp4",
        "bg_type": 1,
        "headline": "Headline 1",
        "description": "Description 1"
    }

    response = api_client.post("/api/brand-page-slice-media-content-blocks/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["custom_name"] == "Media Block 1"
    assert response.data["bg_type"] == 1
    assert "gallery1.jpg" in response.data["bg_image_gallery"][0]


@pytest.mark.django_db
def test_list_brand_page_slice_media_content_blocks(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Media Block List Page",
        slug="media-block-list"
    )

    BrandPageSliceMediaContentBlocks.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Media Block A",
        bg_image="https://example.com/a.jpg",
        bg_image_gallery=["https://example.com/a1.jpg"],
        bg_video="https://example.com/a.mp4",
        bg_type=1,
        headline="Headline A",
        description="Desc A"
    )

    BrandPageSliceMediaContentBlocks.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Media Block B",
        bg_image="https://example.com/b.jpg",
        bg_image_gallery=["https://example.com/b1.jpg"],
        bg_video="https://example.com/b.mp4",
        bg_type=2,
        headline="Headline B",
        description="Desc B"
    )

    response = api_client.get("/api/brand-page-slice-media-content-blocks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_retrieve_brand_page_slice_media_content_block(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Media Block Page",
        slug="retrieve-media-block"
    )

    block = BrandPageSliceMediaContentBlocks.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Retrieve Block",
        bg_image="https://example.com/bg.jpg",
        bg_image_gallery=["https://example.com/g1.jpg"],
        bg_video="https://example.com/vid.mp4",
        bg_type=1,
        headline="Retrieve Headline",
        description="Retrieve Description"
    )

    response = api_client.get(f"/api/brand-page-slice-media-content-blocks/{block.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Retrieve Block"
    assert response.data["headline"] == "Retrieve Headline"


@pytest.mark.django_db
def test_update_brand_page_slice_media_content_block(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Media Block Page",
        slug="update-media-block"
    )

    block = BrandPageSliceMediaContentBlocks.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Old Media Block",
        bg_image="https://example.com/old.jpg",
        bg_image_gallery=["https://example.com/old1.jpg"],
        bg_video="https://example.com/old.mp4",
        bg_type=1,
        headline="Old Headline",
        description="Old Description"
    )

    updated_data = {
        "custom_name": "Updated Media Block",
        "headline": "Updated Headline",
        "description": "Updated Description"
    }

    response = api_client.patch(f"/api/brand-page-slice-media-content-blocks/{block.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Updated Media Block"
    assert response.data["headline"] == "Updated Headline"


@pytest.mark.django_db
def test_delete_brand_page_slice_media_content_block(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Media Block Page",
        slug="delete-media-block"
    )

    block = BrandPageSliceMediaContentBlocks.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Delete Media Block",
        bg_image="https://example.com/delete.jpg",
        bg_image_gallery=["https://example.com/del1.jpg"],
        bg_video="https://example.com/delete.mp4",
        bg_type=1,
        headline="Delete Headline",
        description="Delete Description"
    )

    response = api_client.delete(f"/api/brand-page-slice-media-content-blocks/{block.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSliceMediaContentBlocks.objects.filter(id=block.id).exists()
