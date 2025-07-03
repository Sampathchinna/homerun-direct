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
from organization.models import BrandHeaders  # Add this import if not already present
from organization.serializers import BrandHeadersSerializer  # Add this import if not already present
from organization.viewsets import BrandHeadersViewSet  # Add this import if not already present

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
def test_create_brand_header(api_client, brand):
    payload = {
        "brand": brand.id,
        "meta_tags": {"author": "Admin", "viewport": "width=device-width"},
        "custom_html": "<div>Custom HTML Content</div>"
    }

    response = api_client.post("/api/brand-headers/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["meta_tags"]["author"] == "Admin"
    assert "<div>Custom HTML Content</div>" in response.data["custom_html"]


@pytest.mark.django_db
def test_list_brand_headers(api_client, brand):
    BrandHeaders.objects.create(
        brand=brand,
        meta_tags={"description": "Header 1"},
        custom_html="<header>Header 1</header>"
    )

    BrandHeaders.objects.create(
        brand=brand,
        meta_tags={"description": "Header 2"},
        custom_html="<header>Header 2</header>"
    )

    response = api_client.get("/api/brand-headers/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_retrieve_brand_header(api_client, brand):
    header = BrandHeaders.objects.create(
        brand=brand,
        meta_tags={"description": "Header About"},
        custom_html="<header>About Header</header>"
    )

    response = api_client.get(f"/api/brand-headers/{header.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert "About Header" in response.data["custom_html"]


@pytest.mark.django_db
def test_update_brand_header(api_client, brand):
    header = BrandHeaders.objects.create(
        brand=brand,
        meta_tags={"description": "Old Description"},
        custom_html="<header>Old Header</header>"
    )

    updated_data = {
        "meta_tags": {"description": "Updated Description"},
        "custom_html": "<header>Updated Header</header>"
    }

    response = api_client.patch(f"/api/brand-headers/{header.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["meta_tags"]["description"] == "Updated Description"
    assert "Updated Header" in response.data["custom_html"]


@pytest.mark.django_db
def test_delete_brand_header(api_client, brand):
    header = BrandHeaders.objects.create(
        brand=brand,
        meta_tags={"description": "Delete Me"},
        custom_html="<header>Delete Header</header>"
    )

    response = api_client.delete(f"/api/brand-headers/{header.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandHeaders.objects.filter(id=header.id).exists()





# import pytest
# from rest_framework import status
# from rest_framework.test import APIRequestFactory
# from unittest.mock import patch, MagicMock
# from organization.viewsets import BrandHeadersViewSet
# from organization.models import BrandHeaders
# from organization.serializers import BrandHeadersSerializer
# from rest_framework.request import Request

# @pytest.fixture
# def factory():
#     return APIRequestFactory()


# @pytest.fixture
# def mock_brand_header():
#     mock = MagicMock(spec=BrandHeaders)
#     mock.id = 1
#     mock.brand_id = 1
#     mock.meta_tags = {"key": "value"}
#     mock.custom_html = "<div>test</div>"
#     return mock


# @pytest.fixture
# def mock_serializer(mock_brand_header):
#     serializer = MagicMock(spec=BrandHeadersSerializer)
#     serializer.data = {
#         "id": mock_brand_header.id,
#         "brand": mock_brand_header.brand_id,
#         "meta_tags": mock_brand_header.meta_tags,
#         "custom_html": mock_brand_header.custom_html
#     }
#     return serializer


# # ----------- POSITIVE TESTS -----------
# @patch.object(BrandHeadersViewSet, 'get_queryset')
# @patch.object(BrandHeadersViewSet, 'get_serializer')
# def test_list_brand_headers_success(mock_get_serializer, mock_get_queryset, factory, mock_brand_header):
#     # Setup mock serializer instance
#     mock_serializer_instance = MagicMock()
#     mock_serializer_instance.data = {
#         "brand": 1,
#         "meta_tags": {"key": "value"},
#         "custom_html": "<div>test</div>"
#     }

#     # Mocks
#     mock_get_queryset.return_value = [mock_brand_header]
#     mock_get_serializer.return_value = mock_serializer_instance  # Return a single mock serializer, not a list

#     # View & request
#     view = BrandHeadersViewSet.as_view({'get': 'list'})
#     request = factory.get('/api/brand-headers/?page=1&per_page=5')

#     # Call the view
#     response = view(request)

#     # Assertions
#     assert response.status_code == status.HTTP_200_OK

#     # Verify if the response has both "pagination" and the correct key "responsessss"
#     assert "pagination" in response.data  # Ensure pagination exists
#     assert "responsessss" in response.data  # Update to check for the correct key



# @patch.object(BrandHeadersViewSet, 'get_serializer')
# @patch.object(BrandHeadersViewSet, 'perform_create')
# def test_create_brand_header_success(mock_perform_create, mock_get_serializer, factory, mock_serializer):
#     mock_get_serializer.return_value = mock_serializer
#     view = BrandHeadersViewSet.as_view({'post': 'create'})
#     data = {
#         "brand": 1,
#         "meta_tags": {"key": "value"},
#         "custom_html": "<div>test</div>"
#     }
#     request = factory.post('/api/brand-headers/', data, format='json')
#     response = view(request)
#     assert response.status_code == status.HTTP_201_CREATED


# @patch.object(BrandHeadersViewSet, 'get_object')
# @patch.object(BrandHeadersViewSet, 'get_serializer')
# def test_retrieve_brand_header_success(mock_get_serializer, mock_get_object, factory, mock_brand_header, mock_serializer):
#     view = BrandHeadersViewSet.as_view({'get': 'retrieve'})
#     mock_get_object.return_value = mock_brand_header
#     mock_get_serializer.return_value = mock_serializer

#     request = factory.get('/api/brand-headers/1/')
#     response = view(request, pk=1)
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data == mock_serializer.data


# # ----------- NEGATIVE TESTS -----------

# @patch.object(BrandHeadersViewSet, 'get_queryset')
# def test_list_brand_headers_failure(mock_get_queryset, factory):
#     view = BrandHeadersViewSet.as_view({'get': 'list'})
#     mock_get_queryset.side_effect = Exception("DB error")

#     request = factory.get('/api/brand-headers/')
#     with pytest.raises(Exception):
#         view(request)


# @patch.object(BrandHeadersViewSet, 'get_serializer')
# def test_create_brand_header_failure(mock_get_serializer, factory):
#     view = BrandHeadersViewSet.as_view({'post': 'create'})
#     mock_get_serializer.side_effect = Exception("Serializer Error")

#     data = {
#         "brand": 1,
#         "meta_tags": {"key": "value"},
#         "custom_html": "<div>test</div>"
#     }
#     request = factory.post('/api/brand-headers/', data, format='json')
#     with pytest.raises(Exception):
#         view(request)


# @patch.object(BrandHeadersViewSet, 'get_object')
# def test_retrieve_brand_header_not_found(mock_get_object, factory):
#     view = BrandHeadersViewSet.as_view({'get': 'retrieve'})
#     mock_get_object.side_effect = BrandHeaders.DoesNotExist("Not Found")

#     request = factory.get('/api/brand-headers/999/')
#     with pytest.raises(BrandHeaders.DoesNotExist):
#         view(request, pk=999)












