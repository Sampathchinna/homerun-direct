
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

from organization.models import BrandPageSliceReviews

from rest_framework.test import force_authenticate



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
def test_create_brand_page_slice_review(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Review Page",
        slug="review-page"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "custom_name": "Review Block 1",
        "review_data": {"rating": 5, "comment": "Excellent!"}
    }

    response = api_client.post("/api/brand-page-slice-reviews/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["review_data"]["rating"] == 5
    assert "Excellent" in response.data["review_data"]["comment"]

@pytest.mark.django_db
def test_list_brand_page_slice_reviews(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Review List Page",
        slug="review-list"
    )

    BrandPageSliceReviews.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Review A",
        review_data={"rating": 4, "comment": "Good"}
    )

    BrandPageSliceReviews.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="Review B",
        review_data={"rating": 3, "comment": "Average"}
    )

    response = api_client.get("/api/brand-page-slice-reviews/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2

@pytest.mark.django_db
def test_retrieve_brand_page_slice_review(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Review Page",
        slug="retrieve-review"
    )

    review = BrandPageSliceReviews.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Retrieve Review",
        review_data={"rating": 5, "comment": "Outstanding!"}
    )

    response = api_client.get(f"/api/brand-page-slice-reviews/{review.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["review_data"]["comment"] == "Outstanding!"

@pytest.mark.django_db
def test_update_brand_page_slice_review(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Review Page",
        slug="update-review"
    )

    review = BrandPageSliceReviews.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Old Review",
        review_data={"rating": 2, "comment": "Bad"}
    )

    updated_data = {
        "review_data": {"rating": 4, "comment": "Improved"}
    }

    response = api_client.patch(f"/api/brand-page-slice-reviews/{review.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["review_data"]["comment"] == "Improved"

@pytest.mark.django_db
def test_delete_brand_page_slice_review(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Review Page",
        slug="delete-review"
    )

    review = BrandPageSliceReviews.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Delete Review",
        review_data={"rating": 1, "comment": "Terrible"}
    )

    response = api_client.delete(f"/api/brand-page-slice-reviews/{review.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSliceReviews.objects.filter(id=review.id).exists()
