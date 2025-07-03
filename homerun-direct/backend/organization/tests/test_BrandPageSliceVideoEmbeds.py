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
from organization.models import BrandPageSliceVideoEmbeds
from organization.serializers import BrandPageSliceVideoEmbedsSerializer
from organization.viewsets import BrandPageSliceVideoEmbedsViewSet
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
# -------------------- Tests for BrandPageSliceVideoEmbeds --------------------

@pytest.mark.django_db
def test_create_brand_page_slice_video_embed(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Video Embed Page",
        slug="video-embed-page"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "custom_name": "Video Block 1",
        "video_url": "https://example.com/video.mp4",
        "video_source": 1,
        "width": "800px",
        "justify": 2
    }

    response = api_client.post("/api/brand-page-slice-video-embeds/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["custom_name"] == "Video Block 1"
    assert response.data["video_url"] == "https://example.com/video.mp4"
    assert response.data["width"] == "800px"


@pytest.mark.django_db
def test_list_brand_page_slice_video_embeds(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Video List Page",
        slug="video-list-page"
    )

    BrandPageSliceVideoEmbeds.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Video A",
        video_url="https://example.com/a.mp4",
        video_source=1,
        width="640px",
        justify=0
    )

    BrandPageSliceVideoEmbeds.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Video B",
        video_url="https://example.com/b.mp4",
        video_source=2,
        width="720px",
        justify=1
    )

    response = api_client.get("/api/brand-page-slice-video-embeds/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_retrieve_brand_page_slice_video_embed(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Video Page",
        slug="retrieve-video-page"
    )

    video = BrandPageSliceVideoEmbeds.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Retrieve Video",
        video_url="https://example.com/retrieve.mp4",
        video_source=1,
        width="1024px",
        justify=1
    )

    response = api_client.get(f"/api/brand-page-slice-video-embeds/{video.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Retrieve Video"
    assert response.data["video_url"] == "https://example.com/retrieve.mp4"


@pytest.mark.django_db
def test_update_brand_page_slice_video_embed(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Video Page",
        slug="update-video-page"
    )

    video = BrandPageSliceVideoEmbeds.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Old Video",
        video_url="https://example.com/old.mp4",
        video_source=0,
        width="600px",
        justify=0
    )

    updated_data = {
        "custom_name": "Updated Video",
        "width": "900px"
    }

    response = api_client.patch(f"/api/brand-page-slice-video-embeds/{video.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Updated Video"
    assert response.data["width"] == "900px"


@pytest.mark.django_db
def test_delete_brand_page_slice_video_embed(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Video Page",
        slug="delete-video-page"
    )

    video = BrandPageSliceVideoEmbeds.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Delete Video",
        video_url="https://example.com/delete.mp4",
        video_source=1,
        width="500px",
        justify=1
    )

    response = api_client.delete(f"/api/brand-page-slice-video-embeds/{video.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSliceVideoEmbeds.objects.filter(id=video.id).exists()
