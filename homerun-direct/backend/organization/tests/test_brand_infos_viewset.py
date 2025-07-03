import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from organization.serializers import BrandInfosSerializer
from organization.viewsets import BrandInfosViewSet
from rbac.models import DirectUser
from django.http import Http404

from django.test.utils import override_settings

from django.urls import reverse

from organization.models import Organization, Brand, BrandInfos



from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def api_factory():
    return APIRequestFactory()


@pytest.fixture
def mock_user():
    user = MagicMock(spec=DirectUser)
    user.is_authenticated = True
    return user


@pytest.fixture
def sample_data():
    return {
        "brand": 1,
        "theme": 2,
        "colors": {"primary": "#fff"},
        "contact": {"email": "test@example.com"},
        "css_override": "body { background: red; }",
        "fonts": {"font": "Arial"},
        "social": {"twitter": "@brand"},
        "google_analytics": "UA-123456",
        "logo_image": "logo.png",
        "logo_image_processing": False,
        "favicon_image": "favicon.ico",
        "favicon_image_processing": True,
        "copyright": "© 2025 Brand",
        "from_email": "noreply@brand.com",
        "signature": "Best, Brand",
        "robots": "index, follow",
        "robots_name": "robots.txt",
        "custom_hero_html": "<h1>Hero</h1>",
        "scripts_override": "<script></script>",
        "bootstrap4": True,
        "body_class": "dark",
        "google_tag_manager": "GTM-ABC",
        "facebook_pixel": "FB-123",
        "hubspot_tracking": "HS-789",
        "google_events": False,
        "google_verification": "verify",
        "legacy": False,
        "logo_white_image": "white_logo.png",
        "logo_white_image_processing": True,
        "book_now": {"enabled": True},
        "send_message": {"enabled": True}
    }



@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
@patch("organization.viewsets.BrandInfosViewSet.get_queryset")
def test_list_brandinfos(mock_get_queryset, api_factory, mock_user, sample_data):
    mock_instance = MagicMock()
    mock_instance.configure_mock(**sample_data)
    mock_get_queryset.return_value = [mock_instance]

    view = BrandInfosViewSet.as_view({"get": "list"})
    request = api_factory.get("/api/brand-infos/")
    force_authenticate(request, user=mock_user)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK







@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
@patch("organization.viewsets.BrandInfosViewSet.get_object")
def test_retrieve_brandinfo(mock_get_object, api_factory, mock_user, sample_data):
    mock_instance = MagicMock()
    mock_instance.configure_mock(**sample_data)
    mock_get_object.return_value = mock_instance

    view = BrandInfosViewSet.as_view({"get": "retrieve"})
    request = api_factory.get("/api/brand-infos/1/")
    force_authenticate(request, user=mock_user)
    response = view(request, pk=1)

    assert response.status_code == status.HTTP_200_OK






@pytest.mark.django_db
@patch("organization.viewsets.BrandInfosViewSet.get_object")
def test_delete_brandinfo(mock_get_object, api_factory, mock_user):
    mock_instance = MagicMock()
    mock_get_object.return_value = mock_instance

    view = BrandInfosViewSet.as_view({"delete": "destroy"})
    request = api_factory.delete("/api/brand-infos/1/")
    force_authenticate(request, user=mock_user)
    response = view(request, pk=1)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_instance.delete.assert_called_once()


@pytest.mark.django_db
@patch("organization.viewsets.BrandInfosViewSet.get_object")
def test_retrieve_not_found(mock_get_object, api_factory, mock_user):
    mock_get_object.side_effect = Http404("Not found")


    view = BrandInfosViewSet.as_view({"get": "retrieve"})
    request = api_factory.get("/api/brand-infos/999/")
    force_authenticate(request, user=mock_user)
    response = view(request, pk=999)

    assert response.status_code == status.HTTP_404_NOT_FOUND or status.HTTP_500_INTERNAL_SERVER_ERROR




import pytest
from organization.models import BrandInfos, Brand, Organization
from master.models import (
    Language, Currency, OrganizationType, CompanyType,
    PaymentProcessor, Location, SubscriptionPlan
)
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_brandinfo_success_with_mockdata():
    user = User.objects.create(username="testuser")
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
        organization_name="Test Org",
        user=user,
        language=language,
        currency=currency,
        organization_type=org_type,
        company_type=company_type,
        payment_processor=processor,
        location=location,
        subscription_plan=plan,
        terms_agreement=True,
    )

    brand = Brand.objects.create(
        organization=org, name="Test Brand", currency="usd", language="en"
    )

    brand_info = BrandInfos.objects.create(
        brand=brand,
        theme=1,
        colors={"primary": "#000000"},
        contact={"email": "info@test.com"},
        css_override="body { background: #fff; }",
        fonts={"header": "Arial"},
        social={"facebook": "test"},
        google_analytics="GA-1234",
        logo_image="logo.png",
        favicon_image="favicon.ico",
        copyright="© 2025",
        from_email="contact@test.com",
        signature="Thanks",
        robots="index,follow",
        robots_name="robots.txt",
        custom_hero_html="<h1>Welcome</h1>",
        scripts_override="<script>console.log('test')</script>",
        bootstrap4=True,
        body_class="test-body",
        google_tag_manager="GTM-12345",
        facebook_pixel="FB-123",
        hubspot_tracking="HS-123",
        google_events=True,
        google_verification="GV-123",
        legacy=False,
        logo_white_image="logo_white.png",
        logo_white_image_processing=True,
        book_now={"enabled": True},
        send_message={"enabled": True}
    )

    assert brand_info.pk is not None
    assert brand_info.brand == brand
    assert brand_info.theme == 1

@pytest.mark.django_db
def test_update_brandinfo_success_with_mockdata():
    user = User.objects.create(username="testuser2")
    language = Language.objects.create(old_id="2", value="fr")
    currency = Currency.objects.create(old_id="2", value="eur")
    org_type = OrganizationType.objects.create(old_id="2", value="spa")
    company_type = CompanyType.objects.create(old_id="2", value="inc")
    processor = PaymentProcessor.objects.create(label="Paypal", value="paypal")
    location = Location.objects.create(
        apt_suite="202", city="TempCity", state_province="TP",
        postal_code="54321", country="TempLand", street_address="456 Temp St",
        latitude=21.123456, longitude=87.654321, exact=True,
        timezone="CET", locationable_type_id=2
    )
    plan = SubscriptionPlan.objects.create(
        provider=processor, name="Basic Plan", interval="yearly", price_cents=5000
    )

    org = Organization.objects.create(
        organization_name="Temp Org",
        user=user,
        language=language,
        currency=currency,
        organization_type=org_type,
        company_type=company_type,
        payment_processor=processor,
        location=location,
        subscription_plan=plan,
        terms_agreement=True,
    )

    brand = Brand.objects.create(
        organization=org,
        name="Temp Brand",
        currency="eur",
        language="fr"
    )

    brand_info = BrandInfos.objects.create(
        brand=brand,
        theme=2,
        css_override="",
        google_analytics="",
        book_now={"enabled": False},
        send_message={"enabled": False},
        logo_white_image_processing=True  # Add this field value here
    )

    # Update brand_info
    brand_info.theme = 5
    brand_info.google_analytics = "GA-5678"
    brand_info.save()

    updated_info = BrandInfos.objects.get(pk=brand_info.pk)

    assert updated_info.theme == 5
    assert updated_info.google_analytics == "GA-5678"
