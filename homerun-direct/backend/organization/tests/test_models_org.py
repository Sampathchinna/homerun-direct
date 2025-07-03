import pytest
from django.core.exceptions import ValidationError
from organization.models import Organization
from master.models import Currency, Language, PaymentProcessor, OrganizationType, CompanyType, Location, SubscriptionPlan, LocationableType
from django.contrib.auth import get_user_model

# Setup pytest-django fixtures
@pytest.fixture
def user():
    return get_user_model().objects.create_user(
        username='testuser', password='testpassword', email='testuser@example.com'
    )

@pytest.fixture
def organization_type():
    return OrganizationType.objects.create(old_id="123", value="hotel")

@pytest.fixture
def language():
    return Language.objects.create(old_id="en", value="en")

@pytest.fixture
def currency():
    return Currency.objects.create(old_id="USD", value="usd")

@pytest.fixture
def company_type():
    return CompanyType.objects.create(old_id="corp", value="corporation")

@pytest.fixture
def payment_processor():
    return PaymentProcessor.objects.create(label="Stripe", value="stripe")

@pytest.fixture
def locationable_type():
    return LocationableType.objects.create(name="Office")  # Use the real field name!


@pytest.fixture
def location(locationable_type):
    return Location.objects.create(
        apt_suite="Apt 123", city="New York", state_province="NY", postal_code="10001", country="US", 
        street_address="123 Street", locationable_type=locationable_type
    )

@pytest.fixture
def subscription_plan(payment_processor):
    return SubscriptionPlan.objects.create(
        provider=payment_processor, name="Pro Plan", interval="monthly", price_cents=999
    )

@pytest.mark.django_db
def test_organization_creation(user, organization_type, language, currency, company_type, payment_processor, location, subscription_plan):
    organization = Organization.objects.create(
        organization_name="Test Organization",
        subdomain="test-org",
        user=user,
        organization_type=organization_type,
        language=language,
        currency=currency,
        company_type=company_type,
        payment_processor=payment_processor,
        location=location,
        subscription_plan=subscription_plan,
        terms_agreement=True,
    )
    assert organization.organization_name == "Test Organization"
    assert organization.subdomain == "test-org"
    assert organization.user == user
    assert organization.organization_type == organization_type
    assert organization.language == language
    assert organization.currency == currency
    assert organization.company_type == company_type
    assert organization.payment_processor == payment_processor
    assert organization.location == location
    assert organization.subscription_plan == subscription_plan
    assert organization.terms_agreement is True

# Add other tests as needed, following the same structure for setting locationable_type and location.


@pytest.mark.django_db
def test_unique_organization_name(user, organization_type, language, currency, company_type, payment_processor, location, subscription_plan):
    # Create the first organization
    Organization.objects.create(
        organization_name="Unique Org",
        subdomain="unique-org",
        user=user,
        organization_type=organization_type,
        language=language,
        currency=currency,
        company_type=company_type,
        payment_processor=payment_processor,
        location=location,
        subscription_plan=subscription_plan,
        terms_agreement=True,
    )

    # Try to create another organization with the same name (should raise ValidationError)
    with pytest.raises(ValidationError):
        organization = Organization.objects.create(
            organization_name="Unique Org",
            subdomain="unique-org2",
            user=user,
            organization_type=organization_type,
            language=language,
            currency=currency,
            company_type=company_type,
            payment_processor=payment_processor,
            location=location,
            subscription_plan=subscription_plan,
            terms_agreement=True,
        )

@pytest.mark.django_db
def test_unique_subdomain(user, organization_type, language, currency, company_type, payment_processor, location, subscription_plan):
    # Create the first organization
    Organization.objects.create(
        organization_name="Test Org 1",
        subdomain="testorg1",
        user=user,
        organization_type=organization_type,
        language=language,
        currency=currency,
        company_type=company_type,
        payment_processor=payment_processor,
        location=location,
        subscription_plan=subscription_plan,
        terms_agreement=True,
    )

    # Try to create another organization with the same subdomain (should raise ValidationError)
    with pytest.raises(ValidationError):
        organization = Organization.objects.create(
            organization_name="Test Org 2",
            subdomain="testorg1",  # Duplicate subdomain
            user=user,
            organization_type=organization_type,
            language=language,
            currency=currency,
            company_type=company_type,
            payment_processor=payment_processor,
            location=location,
            subscription_plan=subscription_plan,
            terms_agreement=True,
        )





@pytest.mark.django_db
def test_clean_method(
    location,
    organization_type,
    language,
    currency,
    payment_processor,
    subscription_plan,
    user,
    company_type  # 👈 Add this fixture
):
    # Create an existing unpaid organization
    Organization.objects.create(
        organization_name="First Org",
        organization_type=organization_type,
        company_type=company_type,  # 👈 Required field
        language=language,
        currency=currency,
        payment_processor=payment_processor,
        location=location,
        subscription_plan=subscription_plan,
        terms_agreement=True,
        user=user,
        is_organization_created=True,
        is_payment_done=False,
        subdomain="first-org"
    )

    # Now try to create another unpaid org
    new_org = Organization(
        organization_name="Second Org",
        organization_type=organization_type,
        company_type=company_type,  # 👈 Required field
        language=language,
        currency=currency,
        payment_processor=payment_processor,
        location=location,
        subscription_plan=subscription_plan,
        terms_agreement=True,
        user=user,
        is_organization_created=True,
        is_payment_done=False,
        subdomain="second-org"
    )

    with pytest.raises(ValidationError) as exc_info:
        new_org.clean()

    assert "one organization without payment" in str(exc_info.value)



@pytest.mark.django_db
def test_parent_id_field(user, organization_type, language, currency, company_type, payment_processor, location, subscription_plan):
    organization = Organization.objects.create(
        organization_name="Test Org With Parent",
        subdomain="testorgwithparent",
        user=user,
        organization_type=organization_type,
        language=language,
        currency=currency,
        company_type=company_type,
        payment_processor=payment_processor,
        location=location,
        subscription_plan=subscription_plan,
        terms_agreement=True,
        parent_id=1,  # Migration purpose
    )
    assert organization.parent_id == 1

@pytest.mark.django_db
def test_organization_status_choices(user, organization_type, language, currency, company_type, payment_processor, location, subscription_plan):
    # Create organization with specific status
    organization = Organization.objects.create(
        organization_name="Test Org Status",
        subdomain="testorgstatus",
        user=user,
        organization_type=organization_type,
        language=language,
        currency=currency,
        company_type=company_type,
        payment_processor=payment_processor,
        location=location,
        subscription_plan=subscription_plan,
        terms_agreement=True,
        status="yellow"
    )
    assert organization.status == "yellow"

@pytest.mark.django_db
def test_organization_terms_agreement_false(user, organization_type, language, currency, company_type, payment_processor, location, subscription_plan):
    # Create organization with terms_agreement set to False
    organization = Organization.objects.create(
        organization_name="Test Org No Terms",
        subdomain="testorgnoterms",
        user=user,
        organization_type=organization_type,
        language=language,
        currency=currency,
        company_type=company_type,
        payment_processor=payment_processor,
        location=location,
        subscription_plan=subscription_plan,
        terms_agreement=False,
    )
    assert not organization.terms_agreement

