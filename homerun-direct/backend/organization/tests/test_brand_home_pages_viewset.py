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
from organization.models import BrandHomePages  # Add this import if not already present
from organization.serializers import BrandHomePagesSerializer  # Add this import if not already present
from organization.viewsets import BrandHomePagesViewSet  # Add this import if not already present

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
def test_create_brand_homepage(api_client, brand):
    payload = {
        "brand": brand.id,
        "template": 1,
        "payload": {"header": "Welcome", "body": "This is the homepage."},
        "options": "option1",
        "meta_title": "Homepage Meta Title",
        "meta_description": "Homepage Meta Description",
        "cms_display_name": "CMS Home",
        "title": "Home Title",
        "description": "Home Description"
    }

    response = api_client.post("/api/brand-homepages/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["cms_display_name"] == "CMS Home"
    assert response.data["title"] == "Home Title"
    assert response.data["description"] == "Home Description"


@pytest.mark.django_db
def test_list_brand_homepages(api_client, brand):
    BrandHomePages.objects.create(
        brand=brand,
        template=1,
        payload={"section": "Intro"},
        options="opt1",
        meta_title="Intro Page",
        meta_description="Intro page description",
        cms_display_name="CMS Intro",
        title="Intro Title",
        description="Intro Description"
    )

    BrandHomePages.objects.create(
        brand=brand,
        template=2,
        payload={"section": "Contact"},
        options="opt2",
        meta_title="Contact Page",
        meta_description="Contact page description",
        cms_display_name="CMS Contact",
        title="Contact Title",
        description="Contact Description"
    )

    response = api_client.get("/api/brand-homepages/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_retrieve_brand_homepage(api_client, brand):
    homepage = BrandHomePages.objects.create(
        brand=brand,
        template=1,
        payload={"section": "About"},
        options="opt3",
        meta_title="About Page",
        meta_description="About page description",
        cms_display_name="CMS About",
        title="About Title",
        description="About Description"
    )

    response = api_client.get(f"/api/brand-homepages/{homepage.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["cms_display_name"] == "CMS About"
    assert response.data["title"] == "About Title"


@pytest.mark.django_db
def test_update_brand_homepage(api_client, brand):
    homepage = BrandHomePages.objects.create(
        brand=brand,
        template=1,
        payload={"section": "Services"},
        options="opt4",
        meta_title="Services Page",
        meta_description="Services page description",
        cms_display_name="CMS Services",
        title="Services Title",
        description="Services Description"
    )

    updated_data = {
        "cms_display_name": "CMS Updated Services",
        "title": "Updated Services Title",
        "description": "Updated Services Description"
    }

    response = api_client.patch(f"/api/brand-homepages/{homepage.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["cms_display_name"] == "CMS Updated Services"
    assert response.data["title"] == "Updated Services Title"
    assert response.data["description"] == "Updated Services Description"


@pytest.mark.django_db
def test_delete_brand_homepage(api_client, brand):
    homepage = BrandHomePages.objects.create(
        brand=brand,
        template=1,
        payload={"section": "Delete Me"},
        options="opt5",
        meta_title="Delete Page",
        meta_description="Delete page description",
        cms_display_name="CMS Delete",
        title="Delete Title",
        description="Delete Description"
    )

    response = api_client.delete(f"/api/brand-homepages/{homepage.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandHomePages.objects.filter(id=homepage.id).exists()







