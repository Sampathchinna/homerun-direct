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
from organization.models import BrandPageSliceSingleImages
from organization.serializers import BrandPageSliceSingleImagesSerializer
from organization.viewsets import BrandPageSliceSingleImagesViewSet
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
def test_create_brand_page_slice_single_image(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Single Image Page",
        slug="single-image-page"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "custom_name": "Image Block 1",
        "image_url": "https://example.com/image.jpg",
        "width": 500,
        "justify": 1
    }

    response = api_client.post("/api/brand-page-slice-single-images/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["custom_name"] == "Image Block 1"
    assert response.data["image_url"] == "https://example.com/image.jpg"
    assert response.data["width"] == 500

@pytest.mark.django_db
def test_list_brand_page_slice_single_images(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Image List Page",
        slug="image-list-page"
    )

    BrandPageSliceSingleImages.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Image A",
        image_url="https://example.com/a.jpg",
        width=300,
        justify=0
    )

    BrandPageSliceSingleImages.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Image B",
        image_url="https://example.com/b.jpg",
        width=400,
        justify=1
    )

    response = api_client.get("/api/brand-page-slice-single-images/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2

@pytest.mark.django_db
def test_retrieve_brand_page_slice_single_image(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Image Page",
        slug="retrieve-image-page"
    )

    image = BrandPageSliceSingleImages.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Retrieve Image",
        image_url="https://example.com/retrieve.jpg",
        width=600,
        justify=2
    )

    response = api_client.get(f"/api/brand-page-slice-single-images/{image.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Retrieve Image"
    assert response.data["image_url"] == "https://example.com/retrieve.jpg"

@pytest.mark.django_db
def test_update_brand_page_slice_single_image(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Image Page",
        slug="update-image-page"
    )

    image = BrandPageSliceSingleImages.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Old Image",
        image_url="https://example.com/old.jpg",
        width=200,
        justify=0
    )

    updated_data = {
        "custom_name": "Updated Image",
        "width": 450
    }

    response = api_client.patch(f"/api/brand-page-slice-single-images/{image.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Updated Image"
    assert response.data["width"] == 450

@pytest.mark.django_db
def test_delete_brand_page_slice_single_image(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Image Page",
        slug="delete-image-page"
    )

    image = BrandPageSliceSingleImages.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Delete Image",
        image_url="https://example.com/delete.jpg",
        width=250,
        justify=1
    )

    response = api_client.delete(f"/api/brand-page-slice-single-images/{image.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSliceSingleImages.objects.filter(id=image.id).exists()
