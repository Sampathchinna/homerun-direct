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
from organization.models import BrandsEmployees
from organization.serializers import BrandsEmployeesSerializer
from organization.viewsets import BrandsEmployeesViewSet
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
def test_create_brands_employee(api_client, brand):
    payload = {
        "brand": brand.id,
        "employee_id": 12345,
        "all_id": 54321
    }

    response = api_client.post("/api/brands-employees/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["employee_id"] == 12345
    assert response.data["all_id"] == 54321


@pytest.mark.django_db
def test_list_brands_employees(api_client, brand):
    BrandsEmployees.objects.create(
        brand=brand,
        employee_id=11111,
        all_id=22222
    )
    BrandsEmployees.objects.create(
        brand=brand,
        employee_id=33333,
        all_id=44444
    )

    response = api_client.get("/api/brands-employees/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_retrieve_brands_employee(api_client, brand):
    employee = BrandsEmployees.objects.create(
        brand=brand,
        employee_id=77777,
        all_id=88888
    )

    response = api_client.get(f"/api/brands-employees/{employee.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["employee_id"] == 77777
    assert response.data["all_id"] == 88888


@pytest.mark.django_db
def test_update_brands_employee(api_client, brand):
    employee = BrandsEmployees.objects.create(
        brand=brand,
        employee_id=99999,
        all_id=101010
    )

    updated_data = {
        "employee_id": 11111,
        "all_id": 121212
    }

    response = api_client.patch(f"/api/brands-employees/{employee.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["employee_id"] == 11111
    assert response.data["all_id"] == 121212


@pytest.mark.django_db
def test_delete_brands_employee(api_client, brand):
    employee = BrandsEmployees.objects.create(
        brand=brand,
        employee_id=131313,
        all_id=141414
    )

    response = api_client.delete(f"/api/brands-employees/{employee.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandsEmployees.objects.filter(id=employee.id).exists()
