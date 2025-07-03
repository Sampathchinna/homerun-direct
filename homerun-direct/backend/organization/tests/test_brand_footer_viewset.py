import pytest
from types import SimpleNamespace
from unittest.mock import patch
from rest_framework.test import APIRequestFactory, force_authenticate
from organization.viewsets import BrandFootersViewSet
from organization.models import BrandFooters


@pytest.fixture
def api_factory():
    return APIRequestFactory()


@pytest.fixture
def mock_user():
    return SimpleNamespace(id=1, is_authenticated=True)


# ---------------------- POSITIVE TESTS ----------------------

@patch("organization.viewsets.BrandFootersViewSet.get_queryset")
def test_list_brand_footers_success(mock_get_queryset, api_factory, mock_user):
    mock_brand = SimpleNamespace(pk=1)
    mock_instance = SimpleNamespace(pk=1, scripts="sample", brand=mock_brand)
    mock_get_queryset.return_value = [mock_instance]

    view = BrandFootersViewSet.as_view({"get": "list"})
    request = api_factory.get("/api/brand-footers/")
    force_authenticate(request, user=mock_user)
    response = view(request)

    assert response.status_code == 200


@patch("organization.viewsets.BrandFootersViewSet.get_object")
@patch("organization.viewsets.BrandFootersSerializer")
def test_retrieve_brand_footer_success(mock_serializer_class, mock_get_object, api_factory, mock_user):
    mock_brand = SimpleNamespace(pk=1)
    mock_instance = SimpleNamespace(pk=1, scripts="retrieved", brand=mock_brand)
    mock_get_object.return_value = mock_instance

    mock_serializer = mock_serializer_class.return_value
    mock_serializer.data = {"id": 1, "scripts": "retrieved"}

    view = BrandFootersViewSet.as_view({"get": "retrieve"})
    request = api_factory.get("/api/brand-footers/1/")
    force_authenticate(request, user=mock_user)
    response = view(request, pk=1)

    assert response.status_code == 200
    assert response.data["scripts"] == "retrieved"






# ---------------------- NEGATIVE TESTS ----------------------


def test_list_brand_footers_unauthenticated(api_factory):
    view = BrandFootersViewSet.as_view({"get": "list"})
    request = api_factory.get("/api/brand-footers/")
    response = view(request)

    assert response.status_code == 200  # <- Fix expected value



import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from organization.viewsets import BrandFootersViewSet
from organization.models import Organization, Brand, BrandFooters
from django.contrib.auth import get_user_model
import pytest
from rest_framework.test import APIClient
from organization.models import BrandFooters, Brand, Organization
from django.urls import reverse

User = get_user_model()



import pytest
from master.models import (
    CompanyType,
    PaymentProcessor,
    Language,
    Currency,
    Location,
    LocationableType,
    SubscriptionPlan,
)

# @pytest.fixture
# def setup_master_objects(db):
#     locationable_type = LocationableType.objects.create(name="Organization")

#     return {
#         "company_type": CompanyType.objects.create(old_id="c1", value="corporation"),
#         "payment_processor": PaymentProcessor.objects.create(label="Stripe", value="stripe"),
#         "language": Language.objects.create(old_id="l1", value="en"),
#         "currency": Currency.objects.create(old_id="usd", value="USD"),
#         "location": Location.objects.create(
#             city="New York",
#             state_province="NY",
#             postal_code="10001",
#             country="USA",
#             street_address="123 Broadway",
#             locationable_type=locationable_type
#         ),
#         "subscription_plan": SubscriptionPlan.objects.create(
#             provider=PaymentProcessor.objects.get(value="stripe"),
#             name="Basic Plan",
#             interval="monthly",
#             price_cents=1000
#         ),
#     }


from master.models import OrganizationType  # or wherever it's defined

@pytest.fixture
def setup_master_objects(db):
    locationable_type, _ = LocationableType.objects.get_or_create(name="Organization")

    return {
        "company_type": CompanyType.objects.create(old_id="c1", value="corporation"),
        "payment_processor": PaymentProcessor.objects.create(label="Stripe", value="stripe"),
        "language": Language.objects.create(old_id="l1", value="en"),
        "currency": Currency.objects.create(old_id="usd", value="USD"),
        "location": Location.objects.create(
            city="New York",
            state_province="NY",
            postal_code="10001",
            country="USA",
            street_address="123 Broadway",
            locationable_type=locationable_type
        ),
        "subscription_plan": SubscriptionPlan.objects.create(
            provider=PaymentProcessor.objects.get(value="stripe"),
            name="Basic Plan",
            interval="monthly",
            price_cents=1000
        ),
        "organization_type": OrganizationType.objects.create(old_id="org1", value="bnb")

    }







@pytest.mark.django_db
def test_create_brand_footer_success(setup_master_objects):
    client = APIClient()

    # Step 1: Create an organization
    OrganizationType.objects.create(old_id="org1", value="bnb")
    user = User.objects.create(username="testuser") 
    org = Organization.objects.create(
        organization_name="Test Org",
        
        organization_type=setup_master_objects["organization_type"],
        language=setup_master_objects["language"],
        currency=setup_master_objects["currency"],
        payment_processor=setup_master_objects["payment_processor"],
        location=setup_master_objects["location"],
        subscription_plan=setup_master_objects["subscription_plan"],
        company_type=setup_master_objects["company_type"],
        terms_agreement=True,
        is_organization_created=True,
        user=user
)


    # Step 2: Create a brand under the organization
    brand = Brand.objects.create(name="Test Brand", organization=org)

    # Step 3: Prepare footer data
    data = {
        "brand": brand.id,
        "scripts": "<script>console.log('Hello')</script>",
        "sections": {"footer": "Test footer section"},
        "credit_cards": {"enabled": True, "cards": ["visa", "mastercard"]},
        "intercom_id": "abc123xyz",
        "custom_html": "<div>Custom HTML content</div>"
    }

    # Step 4: Hit the endpoint
    url = reverse('brandfooter-list')  # based on your router basename
    response = client.post(url, data, format="json")

    # Step 5: Assertions
    assert response.status_code == 201
    assert BrandFooters.objects.filter(brand=brand).exists()

    footer = BrandFooters.objects.get(brand=brand)
    assert footer.scripts == data["scripts"]
    assert footer.sections == data["sections"]
    assert footer.credit_cards == data["credit_cards"]
    assert footer.intercom_id == data["intercom_id"]
    assert footer.custom_html == data["custom_html"]









# @pytest.mark.django_db
# def test_update_brand_footer_success(api_factory, mock_user):
#     from organization.models import Brand, BrandFooters

#     brand = Brand.objects.create(name="Brand Update")
#     brand_footer = BrandFooters.objects.create(brand=brand, scripts="old script")

#     view = BrandFootersViewSet.as_view({"put": "update"})
#     payload = {"scripts": "updated script", "brand": brand.id}
#     request = api_factory.put(f"/api/brand-footers/{brand_footer.id}/", payload, format="json")
#     force_authenticate(request, user=mock_user)

#     response = view(request, pk=brand_footer.id)

#     assert response.status_code == 200
#     assert response.data["scripts"] == "updated script"

@pytest.mark.django_db
def test_update_brand_footer_success(api_factory, mock_user, setup_master_objects):
    user = User.objects.create(username="testuser") 
    org = Organization.objects.create(
        organization_name="Test Org",
        organization_type=setup_master_objects["organization_type"],  # fixed
        language=setup_master_objects["language"],
        currency=setup_master_objects["currency"],
        payment_processor=setup_master_objects["payment_processor"],
        location=setup_master_objects["location"],
        subscription_plan=setup_master_objects["subscription_plan"],
        company_type=setup_master_objects["company_type"],
        terms_agreement=True,
        is_organization_created=True,
        user=user
    )

    brand = Brand.objects.create(name="Brand Update", organization=org)
    brand_footer = BrandFooters.objects.create(brand=brand, scripts="old script")

    view = BrandFootersViewSet.as_view({"put": "update"})
    payload = {"scripts": "updated script", "brand": brand.id}
    request = api_factory.put(f"/api/brand-footers/{brand_footer.id}/", payload, format="json")
    force_authenticate(request, user=mock_user)

    response = view(request, pk=brand_footer.id)

    assert response.status_code == 200
    assert response.data["scripts"] == "updated script"







@patch("organization.viewsets.BrandFootersViewSet.get_object")
def test_retrieve_brand_footer_not_found(mock_get_object, api_factory, mock_user):
    mock_get_object.side_effect = Exception("Not Found")

    view = BrandFootersViewSet.as_view({"get": "retrieve"})
    request = api_factory.get("/api/brand-footers/999/")
    force_authenticate(request, user=mock_user)

    with pytest.raises(Exception, match="Not Found"):
        view(request, pk=999)


@patch("organization.viewsets.BrandFootersSerializer")
def test_create_brand_footer_validation_error(mock_serializer_class, api_factory, mock_user):
    mock_serializer = mock_serializer_class.return_value
    mock_serializer.is_valid.return_value = False
    mock_serializer.errors = {"brand": ["This field is required."]}
    mock_serializer_class.return_value.context = {}

    payload = {"scripts": "new"}
    view = BrandFootersViewSet.as_view({"post": "create"})
    request = api_factory.post("/api/brand-footers/", payload, format="json")
    force_authenticate(request, user=mock_user)
    response = view(request)

    assert response.status_code == 400
    assert "brand" in response.data



