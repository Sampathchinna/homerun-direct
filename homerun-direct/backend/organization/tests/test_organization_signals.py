







import pytest
from unittest.mock import patch
from organization.models import Organization
from master.models import (
    Language, Currency, CompanyType, PaymentProcessor, Location, SubscriptionPlan, OrganizationType
)
from django.contrib.auth import get_user_model

User = get_user_model()

# Fixture to create a test user
@pytest.fixture
def test_user():
    return User.objects.create_user(username="testuser", password="password123")

# Fixture to provide necessary organization field values for testing
@pytest.fixture
def required_org_fields():
    payment_processor = PaymentProcessor.objects.create(value="Stripe", label="Stripe")
    return {
        "organization_type": OrganizationType.objects.create(value="Startup", old_id="org001"),
        "language": Language.objects.create(value="EN", old_id="EN"),
        "currency": Currency.objects.create(value="USD", old_id="USD"),
        "company_type": CompanyType.objects.create(value="SaaS"),
        "payment_processor": payment_processor,
        "location": Location.objects.create(city="NYC", locationable_type_id=1),
        "subscription_plan": SubscriptionPlan.objects.create(
            name="Pro", interval="monthly", price_cents=1000, provider=payment_processor
        ),
    }

# Test to ensure reindexing happens when FK is saved
@pytest.mark.django_db
@patch("organization.signals.cache_search.index_instance")
@pytest.mark.parametrize("fk_model, fk_field, fk_kwargs", [
    (Language, "language", {"value": "en", "old_id": "lang001"}),
    (Currency, "currency", {"value": "usd", "old_id": "curr001"}),
    (CompanyType, "company_type", {"value": "saas"}),
    (PaymentProcessor, "payment_processor", {"value": "stripe", "label": "Stripe"}),
    (Location, "location", {"city": "NYC", "locationable_type_id": 1}),
    (SubscriptionPlan, "subscription_plan", {
        "name": "Pro", "interval": "monthly", "price_cents": 1000,
    }),
])
def test_signal_triggers_index_instance_on_fk_save(
    index_mock, fk_model, fk_field, fk_kwargs, required_org_fields, test_user
):
    # Create necessary PaymentProcessor for SubscriptionPlan if needed
    if fk_model.__name__ == "SubscriptionPlan":
        processor = PaymentProcessor.objects.create(label="Stripe", value="stripe")
        fk_kwargs["provider_id"] = processor.id

    # Ensure that we are saving the fk_model instance before linking it to the Organization
    instance = fk_model.objects.create(**fk_kwargs)

    # Create Organization with the necessary fields
    org_data = {
        "organization_name": "Test Org",
        "user": test_user,
        "terms_agreement": True,
        **{k: v for k, v in required_org_fields.items() if k != fk_field},
        fk_field: instance,
    }

    org = Organization.objects.create(**org_data)

    # Ensure that instance.save() will trigger the post_save signal
    instance.save()

    # Confirm that index_instance was called for the Organization
    index_mock.assert_called_with(org, "organization")


# Test to ensure no indexing when no Organization is linked
@pytest.mark.django_db
@patch("organization.signals.cache_search.index_instance")
def test_signal_does_not_index_when_no_organization(index_mock):
    # Create Language and save it without linking to an organization
    lang = Language.objects.create(old_id="lang002", value="fr")
    lang.save()

    # Ensure no signal was triggered
    index_mock.assert_not_called()



