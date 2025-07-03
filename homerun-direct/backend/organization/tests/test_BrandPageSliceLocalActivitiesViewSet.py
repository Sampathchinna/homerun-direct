import pytest
from rest_framework.test import APIClient
from rest_framework import status
from organization.models import Brand, Organization
from master.models import Language, Currency, OrganizationType, CompanyType, PaymentProcessor, Location, SubscriptionPlan
from rbac.models import DirectUser
from organization.models import BrandPages  # Assuming it’s in brand.models
from organization.models import BrandPageSliceLocalActivities


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
def test_create_brand_page_slice_local_activity(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Local Activity Page",
        slug="local-activity"
    )

    payload = {
        "brand_page": brand_page.id,
        "page_sort": 1,
        "custom_name": "Adventure Time",
        "local_activities_data": {
            "activity_type": "hiking",
            "location": "Rocky Mountains"
        }
    }

    response = api_client.post("/api/brand-page-slice-local-activities/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["custom_name"] == "Adventure Time"


@pytest.mark.django_db
def test_list_brand_page_slice_local_activities(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="List Local Activities",
        slug="list-local-activities"
    )

    BrandPageSliceLocalActivities.objects.create(
        brand_page=brand_page,
        page_sort=1,
        custom_name="Fishing Trip",
        local_activities_data={"duration": "2 hours"}
    )
    BrandPageSliceLocalActivities.objects.create(
        brand_page=brand_page,
        page_sort=2,
        custom_name="City Tour",
        local_activities_data={"duration": "4 hours"}
    )

    response = api_client.get("/api/brand-page-slice-local-activities/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 2


@pytest.mark.django_db
def test_retrieve_brand_page_slice_local_activity(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Retrieve Local Activity",
        slug="retrieve-local-activity"
    )

    activity = BrandPageSliceLocalActivities.objects.create(
        brand_page=brand_page,
        page_sort=3,
        custom_name="Museum Visit",
        local_activities_data={"entry_fee": "10 USD"}
    )

    response = api_client.get(f"/api/brand-page-slice-local-activities/{activity.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Museum Visit"


@pytest.mark.django_db
def test_update_brand_page_slice_local_activity(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Update Local Activity",
        slug="update-local-activity"
    )

    activity = BrandPageSliceLocalActivities.objects.create(
        brand_page=brand_page,
        page_sort=4,
        custom_name="Old Name",
        local_activities_data={"info": "test"}
    )

    updated_data = {
        "custom_name": "Updated Name",
        "local_activities_data": {"info": "updated info"}
    }

    response = api_client.patch(f"/api/brand-page-slice-local-activities/{activity.id}/", updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["custom_name"] == "Updated Name"
    assert response.data["local_activities_data"]["info"] == "updated info"


@pytest.mark.django_db
def test_delete_brand_page_slice_local_activity(api_client, brand):
    brand_page = BrandPages.objects.create(
        brand=brand,
        title="Delete Local Activity",
        slug="delete-local-activity"
    )

    activity = BrandPageSliceLocalActivities.objects.create(
        brand_page=brand_page,
        page_sort=5,
        custom_name="To Be Deleted",
        local_activities_data={"delete_flag": True}
    )

    response = api_client.delete(f"/api/brand-page-slice-local-activities/{activity.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not BrandPageSliceLocalActivities.objects.filter(id=activity.id).exists()





# import pytest
# from django.urls import reverse
# from organization.models import BrandPages, BrandPageSliceLocalActivities
# from organization.serializers import BrandPageSliceLocalActivitiesSerializer
# from rest_framework import status


# from unittest.mock import patch, MagicMock
# from rest_framework.test import APIRequestFactory, force_authenticate, APIClient


# from organization.models import Brand, Organization
# from master.models import Language, Currency, OrganizationType, CompanyType, PaymentProcessor, Location, SubscriptionPlan
# from rbac.models import DirectUser
# from organization.models import BrandPages  # Assuming it’s in brand.models

# from unittest.mock import patch






# @pytest.fixture
# def api_factory():
#     return APIRequestFactory()

# @pytest.fixture
# def api_client():
#     return APIClient()

# @pytest.fixture
# def mock_user():
#     user = MagicMock(spec=DirectUser)
#     user.is_authenticated = True
#     return user

# @pytest.fixture
# def brand():
#     user = DirectUser.objects.create(username="testuser")
#     language = Language.objects.create(old_id="1", value="en")
#     currency = Currency.objects.create(old_id="1", value="usd")
#     org_type = OrganizationType.objects.create(old_id="1", value="hotel")
#     company_type = CompanyType.objects.create(old_id="1", value="llc")
#     processor = PaymentProcessor.objects.create(label="Stripe", value="stripe")
#     location = Location.objects.create(
#         apt_suite="101", city="TestCity", state_province="TS",
#         postal_code="12345", country="TestLand", street_address="123 Test St",
#         latitude=12.345678, longitude=98.765432, exact=True,
#         timezone="UTC", locationable_type_id=1
#     )
#     plan = SubscriptionPlan.objects.create(
#         provider=processor, name="Pro Plan", interval="monthly", price_cents=1000
#     )
#     org = Organization.objects.create(
#         organization_name="Test Org", user=user, language=language,
#         currency=currency, organization_type=org_type,
#         company_type=company_type, payment_processor=processor,
#         location=location, subscription_plan=plan, terms_agreement=True,
#     )
#     return Brand.objects.create(organization=org, name="Brand1", currency="usd", language="en")





# @pytest.fixture
# def brand_page(brand):
#     return BrandPages.objects.create(brand=brand, title="Sample Brand Page")

# @pytest.fixture
# def local_activity(brand_page):
#     return BrandPageSliceLocalActivities.objects.create(
#         brand_page=brand_page,
#         page_sort=1,
#         custom_name="Local Tour",
#         local_activities_data={"activity": "Hiking", "location": "Hilltop"},
#     )

# @pytest.mark.django_db
# def test_list_local_activities(api_client, mock_user, local_activity):
#     url = reverse('brandpageslicelocalactivity-list')
#     api_client.force_authenticate(user=mock_user)
#     response = api_client.get(url)

#     print("API response:", response.data)  # <-- Add this for debugging

#     assert response.status_code == status.HTTP_200_OK



# @pytest.mark.django_db
# def test_create_local_activity(api_client, mock_user, brand_page):
#     url = reverse('brandpageslicelocalactivity-list')
#     api_client.force_authenticate(user=mock_user)
#     payload = {
#         "brand_page": brand_page.id,
#         "page_sort": 2,
#         "custom_name": "Museum Visit",
#         "local_activities_data": {"activity": "Visit", "location": "Museum"}
#     }
#     response = api_client.post(url, payload, format='json')

#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.data['custom_name'] == "Museum Visit"

# @pytest.mark.django_db
# def test_retrieve_local_activity(api_client, mock_user, local_activity):
#     url = reverse('brandpageslicelocalactivity-detail', args=[local_activity.id])
#     api_client.force_authenticate(user=mock_user)
#     response = api_client.get(url)

#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['custom_name'] == "Local Tour"

# @pytest.mark.django_db
# def test_update_local_activity(api_client, mock_user, local_activity):
#     url = reverse('brandpageslicelocalactivity-detail', args=[local_activity.id])
#     api_client.force_authenticate(user=mock_user)
#     update_data = {
#         "brand_page": local_activity.brand_page.id,
#         "page_sort": 1,
#         "custom_name": "Updated Tour",
#         "local_activities_data": {"activity": "Updated Hiking", "location": "Updated Hilltop"}
#     }
#     response = api_client.put(url, update_data, format='json')

#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['custom_name'] == "Updated Tour"

# @pytest.mark.django_db
# def test_delete_local_activity(api_client, mock_user, local_activity):
#     url = reverse('brandpageslicelocalactivity-detail', args=[local_activity.id])
#     api_client.force_authenticate(user=mock_user)
#     response = api_client.delete(url)

#     assert response.status_code == status.HTTP_204_NO_CONTENT
#     assert BrandPageSliceLocalActivities.objects.count() == 0
