import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from rbac.models import DirectUser, OrganizatioRole, AuthEntityPermission
from organization.models import Organization, OrganizationType
from core.models import Entity
from master.models import Language, Currency, PaymentProcessor, Location, SubscriptionPlan, CompanyType

User = get_user_model()

@pytest.fixture
def basic_user(db):
    return User.objects.create_user(username="basicuser", email="basic@example.com", password="testpass")





from master.models import LocationableType  # make sure this import is there too

@pytest.fixture
def basic_org_related_data(db):
    payment_processor = PaymentProcessor.objects.create(
        label="Stripe Payment",
        value="stripe"
    )
    locationable_type = LocationableType.objects.create(name="org")

    return {
        "organization_type": OrganizationType.objects.create(old_id="ot1", value="bnb"),
        "language": Language.objects.create(old_id="lang1", value="en"),
        "currency": Currency.objects.create(old_id="cur1", value="usd"),
        "company_type": CompanyType.objects.create(old_id="comp1", value="llc"),
        "payment_processor": payment_processor,
        "location": Location.objects.create(
            city="New York",
            state_province="NY",
            country="USA",
            postal_code="10001",
            street_address="5th Avenue",
            latitude="40.7128",
            longitude="-74.0060",
            locationable_type=locationable_type,
            raw_json={"source": "test"},
        ),
        "subscription_plan": SubscriptionPlan.objects.create(
            provider=payment_processor,
            name="Basic Plan",
            interval="monthly",
            price_cents=1000
        ),
    }







@pytest.mark.django_db
def test_create_direct_user():
    user = DirectUser.objects.create_user(
        username="testuser",
        password="testpass123",
        email="test@example.com",
        phone_number="1234567890",
        telephone="123-456",
        name="Test User",
        encrypted_password="encrypted123"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.phone_number == "1234567890"
    assert user.__str__() == "testuser"

@pytest.mark.django_db
def test_email_uniqueness():
    DirectUser.objects.create_user(username="user1", email="unique@example.com", password="pass")
    with pytest.raises(IntegrityError):
        DirectUser.objects.create_user(username="user2", email="unique@example.com", password="pass")

@pytest.mark.django_db
def test_organizatio_role_str(basic_user, basic_org_related_data):
    org = Organization.objects.create(
        organization_name="TechForing",
        subdomain="techforing",
        user=basic_user,
        is_payment_done=True,
        **basic_org_related_data
    )
    role = OrganizatioRole.objects.create(organization=org, name="Employee")
    assert str(role) == "TechForing - Employee"

    no_org_role = OrganizatioRole.objects.create(name="Guest", organization=None)
    assert str(no_org_role) == "None - Guest"

@pytest.mark.django_db
def test_auth_entity_permission_str_and_uniqueness(basic_user, basic_org_related_data):
    org = Organization.objects.create(
        organization_name="TestOrg",
        subdomain="testorg",
        user=basic_user,
        is_payment_done=True,
        **basic_org_related_data
    )
    role = OrganizatioRole.objects.create(organization=org, name="Employee")
    entity = Entity.objects.create(name="TestEntity", model_path="rbac.DirectUser")  # <- FIXED

    perm = AuthEntityPermission.objects.create(
        organization=org,
        group=role,
        entity_name=entity,
        can_create=True,
        can_read=True,
        can_update=False,
        can_delete=False,
        custom_permissions={"export": True}
    )
    assert str(perm) == "TestOrg - Employee - TestEntity"
    assert perm.custom_permissions["export"] is True

    with pytest.raises(IntegrityError):
        AuthEntityPermission.objects.create(
            organization=org,
            group=role,
            entity_name=entity
        )


@pytest.mark.django_db
def test_nullable_fields_in_direct_user():
    user = DirectUser.objects.create_user(
        username="nullable_user",
        password="pass",
        email="nullable@example.com"
    )
    assert user.phone_number is None
    assert user.telephone is None
    assert user.rvshare_user_id is None
    assert user.stripe_plan_id is None






