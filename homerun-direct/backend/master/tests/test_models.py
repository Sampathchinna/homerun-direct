import pytest
from master.models import (
    Currency, CurrencyChoices,
    Language, LanguageChoices,
    OrganizationType, OrganizationTypeChoices,
    CompanyType, CompanyTypeChoices,
    PaymentProcessor, PaymentProcessorType,
    LocationableType, Location,
    SubscriptionPlan
)


pytestmark = pytest.mark.django_db

# ---------- FIXTURES ----------

@pytest.fixture
def payment_processor():
    return PaymentProcessor.objects.create(label="Stripe Gateway", value=PaymentProcessorType.STRIPE)

@pytest.fixture
def locationable_type():
    return LocationableType.objects.create(name="Hotel")

# ---------- POSITIVE TEST CASES ----------

def test_currency_creation():
    currency = Currency.objects.create(old_id="1", value=CurrencyChoices.USD)
    assert currency.value == CurrencyChoices.USD

def test_language_creation():
    lang = Language.objects.create(old_id="2", value=LanguageChoices.EN)
    assert lang.value == LanguageChoices.EN

def test_organization_type_creation():
    org_type = OrganizationType.objects.create(old_id="3", value=OrganizationTypeChoices.HOTEL)
    assert org_type.value == OrganizationTypeChoices.HOTEL

def test_company_type_creation():
    comp_type = CompanyType.objects.create(old_id="4", value=CompanyTypeChoices.LLC)
    assert comp_type.value == CompanyTypeChoices.LLC

def test_payment_processor_creation():
    processor = PaymentProcessor.objects.create(label="Lynnbrook", value=PaymentProcessorType.LYNBROOK)
    assert processor.value == PaymentProcessorType.LYNBROOK

def test_locationable_type_creation():
    location_type = LocationableType.objects.create(name="Apartment")
    assert location_type.name == "Apartment"

def test_location_creation(locationable_type):
    location = Location.objects.create(
        city="New York",
        state_province="NY",
        country="USA",
        postal_code="10001",
        street_address="123 Broadway",
        locationable_type=locationable_type
    )
    assert location.city == "New York"

def test_subscription_plan_creation(payment_processor):
    plan = SubscriptionPlan.objects.create(
        provider=payment_processor,
        name="Pro Plan",
        interval="monthly",
        price_cents=1999
    )
    assert plan.name == "Pro Plan"
    assert plan.interval == "monthly"

# ---------- NEGATIVE TEST CASES ----------

def test_currency_invalid_value():
    from django.core.exceptions import ValidationError
    currency = Currency(old_id="5", value="xyz")
    with pytest.raises(ValidationError):
        currency.full_clean()
        currency.save()

def test_language_empty_value():
    from django.core.exceptions import ValidationError
    lang = Language(old_id="6", value="")
    with pytest.raises(ValidationError):
        lang.full_clean()
        lang.save()


def test_organization_type_invalid_choice():
    from django.core.exceptions import ValidationError
    org_type = OrganizationType(old_id="7", value="motel")
    with pytest.raises(ValidationError):
        org_type.full_clean()
        org_type.save()


def test_company_type_null_value():
    from django.core.exceptions import ValidationError
    comp = CompanyType(old_id="8", value=None)
    with pytest.raises(ValidationError):
        comp.full_clean()
        comp.save()

def test_payment_processor_duplicate_value():
    PaymentProcessor.objects.create(label="Stripe A", value="stripe")
    with pytest.raises(Exception):
        PaymentProcessor.objects.create(label="Stripe B", value="stripe")  # value is unique

def test_locationable_type_duplicate_name():
    LocationableType.objects.create(name="Cabin")
    with pytest.raises(Exception):
        LocationableType.objects.create(name="Cabin")  # name is unique

def test_location_missing_fk():
    with pytest.raises(Exception):
        Location.objects.create(city="Paris")

def test_subscription_plan_invalid_interval(payment_processor):
    from django.core.exceptions import ValidationError
    plan = SubscriptionPlan(
        provider=payment_processor,
        name="Weekly Plan",
        interval="weekly",  # invalid
        price_cents=500
    )
    with pytest.raises(ValidationError):
        plan.full_clean()
        plan.save()








# from django.test import TestCase
# from master.models import Language, Currency, CompanyType, PaymentProcessor, Location, SubscriptionPlan, PaymentProcessorType


# class LanguageModelTest(TestCase):

#     def setUp(self):
#         self.language = Language.objects.create(label="English", value="en")

#     def test_language_creation(self):
#         self.assertEqual(self.language.label, "English")
#         self.assertEqual(self.language.value, "en")

#     def test_language_str_representation(self):
#         self.assertEqual(str(self.language), "en")


# class CurrencyModelTest(TestCase):

#     def setUp(self):
#         self.currency = Currency.objects.create(label="US Dollar", value="USD")

#     def test_currency_creation(self):
#         self.assertEqual(self.currency.label, "US Dollar")
#         self.assertEqual(self.currency.value, "USD")

#     def test_currency_str_representation(self):
#         self.assertEqual(str(self.currency), "USD")


# class CompanyTypeModelTest(TestCase):

#     def setUp(self):
#         self.company_type = CompanyType.objects.create(label="Private", value="private")

#     def test_company_type_creation(self):
#         self.assertEqual(self.company_type.label, "Private")
#         self.assertEqual(self.company_type.value, "private")

#     def test_company_type_str_representation(self):
#         self.assertEqual(str(self.company_type), "private")


# class PaymentProcessorModelTest(TestCase):

#     def setUp(self):
#         self.payment_processor = PaymentProcessor.objects.create(label="Stripe", value=PaymentProcessorType.STRIPE)

#     def test_payment_processor_creation(self):
#         self.assertEqual(self.payment_processor.label, "Stripe")
#         self.assertEqual(self.payment_processor.value, PaymentProcessorType.STRIPE)

#     def test_payment_processor_str_representation(self):
#         self.assertEqual(str(self.payment_processor), "stripe")


# class LocationModelTest(TestCase):

#     def setUp(self):
#         self.location = Location.objects.create(city="New York", state_province="NY", country="USA")

#     def test_location_creation(self):
#         self.assertEqual(self.location.city, "New York")
#         self.assertEqual(self.location.state_province, "NY")
#         self.assertEqual(self.location.country, "USA")

#     def test_location_str_representation(self):
#         self.assertEqual(str(self.location), "New York")


# class SubscriptionPlanModelTest(TestCase):

#     def setUp(self):
#         self.processor = PaymentProcessor.objects.create(label="Stripe", value=PaymentProcessorType.STRIPE)
#         self.subscription_plan = SubscriptionPlan.objects.create(provider=self.processor, name="Pro", interval="monthly", price_cents=1000)

#     def test_subscription_plan_creation(self):
#         self.assertEqual(self.subscription_plan.name, "Pro")
#         self.assertEqual(self.subscription_plan.interval, "monthly")
#         self.assertEqual(self.subscription_plan.price_cents, 1000)
#         self.assertEqual(self.subscription_plan.provider.label, "Stripe")

#     def test_subscription_plan_str_representation(self):
#         self.assertEqual(str(self.subscription_plan), "Pro (monthly) - stripe")






