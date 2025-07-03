import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from organization.models import Organization ,Brand
from master.models import (
    OrganizationType,CompanyType, Currency, Language, Location,
    LocationableType, PaymentProcessor, SubscriptionPlan
)

User = get_user_model()


@pytest.fixture
def user(db):
    # supply both username & email
    return User.objects.create_user(
        username="testuser",
        email="user@example.com",
        password="testpass123"
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def master_data(db):
    """
    Create all required master records and return them in a dict.
    """
    # OrganizationType
    org_type = OrganizationType.objects.create(old_id="1", value="hotel")

    # CompanyType
    comp_type = CompanyType.objects.create(old_id="1", value="corporation")

    # Language & Currency
    lang = Language.objects.create(old_id="en", value="en")
    curr = Currency.objects.create(old_id="usd", value="usd")

    # PaymentProcessor
    pp = PaymentProcessor.objects.create(label="Stripe", value="stripe")

    # LocationableType & Location
    lot = LocationableType.objects.get_or_create(name="Organization")[0]
    loc = Location.objects.create(
        apt_suite="Apt 1",
        city="Testville",
        state_province="Teststate",
        postal_code="12345",
        country="Testland",
        street_address="123 Main St",
        latitude=12.345678,
        longitude=98.765432,
        locationable_type=lot,
        raw_json={"foo": "bar"}
    )

    # SubscriptionPlan
    plan = SubscriptionPlan.objects.create(
        provider=pp,
        name="Test Plan",
        interval="monthly",
        price_cents=1000
    )

    return {
        "organization_type": org_type,
        "company_type": comp_type,
        "language": lang,
        "currency": curr,
        "payment_processor": pp,
        "location": loc,
        "subscription_plan": plan,
    }


@pytest.fixture
def organization_payload(master_data):
    return {
        "organization_name": "Test Org",
        "subdomain": "testorg",
        "description": "A test organization",
        "terms_agreement": True,
        "organization_type": master_data["organization_type"].id,
        "company_type": master_data["company_type"].id,
        "language": master_data["language"].id,
        "currency": master_data["currency"].id,
        "payment_processor": master_data["payment_processor"].id,
        "location": master_data["location"].id,
        "subscription_plan": master_data["subscription_plan"].id,
    }


@pytest.fixture
def brand_payload(master_data):
    return {
        "organization": master_data["organization_type"].id,  # assuming organization created from OrganizationType
        "name": "Test Brand",
        "description": "This is a test brand",
        "currency": "USD",
        "language": "EN",
        "date_format": "MM/DD/YYYY",
        "default": True,
        "tax_rate": "10.50",
        "verify_image": "verify.png",
        "verify_image_description": "Verification image description",
        "verify_signature": "signature.png",
        "settings": {"theme": "dark"},
        "rate_inflator": "1.10",
        "cms_version": "v1.0"
    }

@pytest.mark.django_db
class TestBrandViewSet:

    def test_create_brand(self, auth_client, organization_payload, brand_payload):
        # First create organization because Brand needs it
        org_resp = auth_client.post(reverse("organization-list"), organization_payload, format="json")
        org_id = org_resp.data.get("id") or org_resp.data.get("organization_id")
        
        brand_payload["organization"] = org_id

        url = reverse("brand-list")
        resp = auth_client.post(url, brand_payload, format="json")

        assert resp.status_code == status.HTTP_201_CREATED
        assert Brand.objects.filter(name="Test Brand").exists()

    def test_list_brands(self, auth_client, organization_payload, brand_payload):
        org_resp = auth_client.post(reverse("organization-list"), organization_payload, format="json")
        org_id = org_resp.data.get("id") or org_resp.data.get("organization_id")

        brand_payload["organization"] = org_id
        auth_client.post(reverse("brand-list"), brand_payload, format="json")

        resp = auth_client.get(reverse("brand-list"))
        assert resp.status_code == status.HTTP_200_OK
        data = resp.data.get("response", [])  # Custom list response
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_retrieve_brand(self, auth_client, organization_payload, brand_payload):
        org_resp = auth_client.post(reverse("organization-list"), organization_payload, format="json")
        org_id = org_resp.data.get("id") or org_resp.data.get("organization_id")

        brand_payload["organization"] = org_id
        create = auth_client.post(reverse("brand-list"), brand_payload, format="json")
        brand_id = create.data.get("id")

        url = reverse("brand-detail", args=[brand_id])
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["name"] == "Test Brand"

    def test_update_brand(self, auth_client, organization_payload, brand_payload):
        org_resp = auth_client.post(reverse("organization-list"), organization_payload, format="json")
        org_id = org_resp.data.get("id") or org_resp.data.get("organization_id")

        brand_payload["organization"] = org_id
        create = auth_client.post(reverse("brand-list"), brand_payload, format="json")
        brand_id = create.data.get("id")

        url = reverse("brand-detail", args=[brand_id])
        update_payload = {"name": "Updated Brand", "default": False}

        resp = auth_client.patch(url, update_payload, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["name"] == "Updated Brand"

    def test_delete_brand(self, auth_client, organization_payload, brand_payload):
        org_resp = auth_client.post(reverse("organization-list"), organization_payload, format="json")
        org_id = org_resp.data.get("id") or org_resp.data.get("organization_id")

        brand_payload["organization"] = org_id
        create = auth_client.post(reverse("brand-list"), brand_payload, format="json")
        brand_id = create.data.get("id")

        url = reverse("brand-detail", args=[brand_id])

        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not Brand.objects.filter(id=brand_id).exists()







