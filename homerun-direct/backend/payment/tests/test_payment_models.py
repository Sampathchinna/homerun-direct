import pytest
from django.contrib.auth import get_user_model
from master.models import (
    Currency, Language, OrganizationType, CompanyType,
    PaymentProcessor, LocationableType, Location
)
from organization.models import Organization
from payment.models import StripeCustomer

User = get_user_model()

@pytest.mark.django_db
def test_stripe_customer_creation():
    user = User.objects.create(username="testuser")

    # Required master entries
    currency = Currency.objects.create(old_id="1", value="USD")
    language = Language.objects.create(old_id="1", value="EN")
    org_type = OrganizationType.objects.create(old_id="1", value="bnb")
    company_type = CompanyType.objects.create(old_id="1", value="llc")
    processor = PaymentProcessor.objects.create(label="Stripe", value="stripe")
    loc_type = LocationableType.objects.create(name="Headquarters")
    location = Location.objects.create(
        city="New York",
        country="USA",
        locationable_type=loc_type
    )

    organization = Organization.objects.create(
        organization_name="My Org",
        organization_type=org_type,
        language=language,
        currency=currency,
        company_type=company_type,
        payment_processor=processor,
        location=location,
        user=user,
        confirmed=True
    )

    stripe_customer = StripeCustomer.objects.create(
        user=user,
        organization=organization,
        stripe_customer_id="cus_12345",
        stripe_subscription_id="sub_67890",
        stripe_payment_method_id="pm_abc123",
        stripe_price_id="price_xyz",
        latest_invoice_url="https://stripe.com/invoice/test",
        subscription_status="active"
    )

    assert stripe_customer.pk is not None
    assert stripe_customer.subscription_status == "active"
    assert stripe_customer.organization == organization

import pytest
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_invalid_subscription_status():
    user = User.objects.create(username="invalid_status_user")

    currency = Currency.objects.create(old_id="1", value="USD")
    language = Language.objects.create(old_id="1", value="EN")
    org_type = OrganizationType.objects.create(old_id="1", value="bnb")
    company_type = CompanyType.objects.create(old_id="1", value="llc")
    processor = PaymentProcessor.objects.create(label="Stripe", value="stripe")
    loc_type = LocationableType.objects.create(name="HQ")
    location = Location.objects.create(
        city="Chicago",
        country="USA",
        locationable_type=loc_type
    )

    organization = Organization.objects.create(
        organization_name="Invalid Org",
        organization_type=org_type,
        language=language,
        currency=currency,
        company_type=company_type,
        payment_processor=processor,
        location=location,
        user=user,
        confirmed=True
    )

    stripe_customer = StripeCustomer(
        user=user,
        organization=organization,
        stripe_customer_id="cus_invalid",
        subscription_status="wrong_status"  # Not valid
    )

    with pytest.raises(ValidationError) as exc_info:
        stripe_customer.full_clean()  # This triggers validation

    assert "subscription_status" in str(exc_info.value)


# @pytest.mark.django_db
# def test_invalid_subscription_status():
#     user = User.objects.create(username="invalid_status_user")

#     currency = Currency.objects.create(old_id="1", value="USD")
#     language = Language.objects.create(old_id="1", value="EN")
#     org_type = OrganizationType.objects.create(old_id="1", value="bnb")
#     company_type = CompanyType.objects.create(old_id="1", value="llc")
#     processor = PaymentProcessor.objects.create(label="Stripe", value="stripe")
#     loc_type = LocationableType.objects.create(name="HQ")
#     location = Location.objects.create(
#         city="Chicago",
#         country="USA",
#         locationable_type=loc_type
#     )

#     organization = Organization.objects.create(
#         organization_name="Invalid Org",
#         organization_type=org_type,
#         language=language,
#         currency=currency,
#         company_type=company_type,
#         payment_processor=processor,
#         location=location,
#         user=user,
#         confirmed=True
#     )

#     with pytest.raises(ValueError):
#         StripeCustomer.objects.create(
#             user=user,
#             organization=organization,
#             stripe_customer_id="cus_invalid",
#             subscription_status="wrong_status"  # Not in choices
#         )

@pytest.mark.django_db
def test_missing_stripe_customer_id():
    user = User.objects.create(username="missing_fields")

    currency = Currency.objects.create(old_id="1", value="USD")
    language = Language.objects.create(old_id="1", value="EN")
    org_type = OrganizationType.objects.create(old_id="1", value="bnb")
    company_type = CompanyType.objects.create(old_id="1", value="llc")
    processor = PaymentProcessor.objects.create(label="Stripe", value="stripe")
    loc_type = LocationableType.objects.create(name="HQ")
    location = Location.objects.create(
        city="Boston",
        country="USA",
        locationable_type=loc_type
    )

    organization = Organization.objects.create(
        organization_name="Org Missing Fields",
        organization_type=org_type,
        language=language,
        currency=currency,
        company_type=company_type,
        payment_processor=processor,
        location=location,
        user=user,
        confirmed=True
    )

    with pytest.raises(Exception):
        StripeCustomer.objects.create(
            user=user,
            organization=organization,
            stripe_customer_id=None,  # Required field is missing
            subscription_status="active"
        )
