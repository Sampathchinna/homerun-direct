import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient
from rest_framework import status
from organization.models import Brand, Organization
from master.models import Language, Currency, OrganizationType, CompanyType, PaymentProcessor, Location, SubscriptionPlan
from rbac.models import DirectUser
from organization.models import BrandPages  # Assuming it’s in brand.models

from organization.models import BrandPageSliceHomepageHeros


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
def test_create_brand_page_slice_homepage_hero(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Homepage Hero Page",
        slug="homepage-hero"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "custom_name": "Hero Block 1",
        "bg_image": "image_url",
        "bg_image_gallery": ["image_url1", "image_url2"],
        "bg_video": "video_url",
        "bg_type": 1,
        "headline": "Welcome to Our Brand!",
        "description": "This is the hero section.",
        "layout_type": 1
    }

    response = api_client.post("/api/brand-page-slice-homepage-heros/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["custom_name"] == "Hero Block 1"
    assert response.data["bg_image"] == "image_url"
    assert response.data["headline"] == "Welcome to Our Brand!"
    assert response.data["layout_type"] == 1


@pytest.mark.django_db
def test_list_brand_page_slice_homepage_heros(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="List Homepage Heroes",
        slug="list-homepage-hero"
    )

    BrandPageSliceHomepageHeros.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Hero Block A",
        bg_image="image_url_a",
        bg_image_gallery=["image_a1", "image_a2"],
        bg_video="video_a_url",
        bg_type=1,
        headline="Hero A Headline",
        description="Description A",
        layout_type=1
    )
    BrandPageSliceHomepageHeros.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Hero Block B",
        bg_image="image_url_b",
        bg_image_gallery=["image_b1", "image_b2"],
        bg_video="video_b_url",
        bg_type=2,
        headline="Hero B Headline",
        description="Description B",
        layout_type=2
    )

    response = api_client.get("/api/brand-page-slice-homepage-heros/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_retrieve_brand_page_slice_homepage_hero(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Homepage Hero",
        slug="retrieve-homepage-hero"
    )

    hero = BrandPageSliceHomepageHeros.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Hero Block X",
        bg_image="image_url_x",
        bg_image_gallery=["image_x1", "image_x2"],
        bg_video="video_x_url",
        bg_type=1,
        headline="Hero X Headline",
        description="Description X",
        layout_type=1
    )

    response = api_client.get(f"/api/brand-page-slice-homepage-heros/{hero.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Hero Block X"
    assert response.data["bg_image"] == "image_url_x"
    assert response.data["headline"] == "Hero X Headline"


@pytest.mark.django_db
def test_update_brand_page_slice_homepage_hero(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Homepage Hero",
        slug="update-homepage-hero"
    )

    hero = BrandPageSliceHomepageHeros.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Old Hero Block",
        bg_image="old_image_url",
        bg_image_gallery=["old_image1", "old_image2"],
        bg_video="old_video_url",
        bg_type=1,
        headline="Old Hero Headline",
        description="Old Description",
        layout_type=1
    )

    updated_data = {
        "custom_name": "Updated Hero Block",
        "bg_image": "new_image_url",
        "bg_image_gallery": ["new_image1", "new_image2"],
        "bg_video": "new_video_url",
        "bg_type": 2,
        "headline": "Updated Hero Headline",
        "description": "Updated Description",
        "layout_type": 2
    }

    response = api_client.patch(f"/api/brand-page-slice-homepage-heros/{hero.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Updated Hero Block"
    assert response.data["bg_image"] == "new_image_url"
    assert response.data["headline"] == "Updated Hero Headline"
    assert response.data["layout_type"] == 2


@pytest.mark.django_db
def test_delete_brand_page_slice_homepage_hero(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Homepage Hero",
        slug="delete-homepage-hero"
    )

    hero = BrandPageSliceHomepageHeros.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Hero Block to Delete",
        bg_image="delete_image_url",
        bg_image_gallery=["delete_image1", "delete_image2"],
        bg_video="delete_video_url",
        bg_type=1,
        headline="Hero to Delete Headline",
        description="Hero to Delete Description",
        layout_type=1
    )

    response = api_client.delete(f"/api/brand-page-slice-homepage-heros/{hero.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSliceHomepageHeros.objects.filter(id=hero.id).exists()
