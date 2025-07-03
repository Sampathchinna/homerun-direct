import pytest
from unittest.mock import patch

from master.signals import (
    insert_languages_and_currencies,
    insert_locationable_types,
    insert_company_types,
    insert_organization_types,
    insert_master_data
)

from master.models import Currency, Language, LocationableType, CompanyType, OrganizationType


@pytest.mark.django_db
def test_insert_languages_and_currencies_creates_all_entries():
    insert_languages_and_currencies(sender=None)

    assert Currency.objects.count() == 22
    assert Language.objects.count() == 28

    assert Currency.objects.filter(value='usd').exists()
    assert Language.objects.filter(value='en').exists()


@pytest.mark.django_db
def test_insert_locationable_types_creates_all_entries():
    insert_locationable_types(sender=None)

    assert LocationableType.objects.count() == 9
    assert LocationableType.objects.filter(name='Organization').exists()


@pytest.mark.django_db
def test_insert_company_types_creates_all_entries():
    insert_company_types(sender=None)

    assert CompanyType.objects.count() == 6
    llc = CompanyType.objects.get(value='llc')
    assert llc.old_id == '4'


@pytest.mark.django_db
def test_insert_organization_types_creates_all_entries():
    insert_organization_types(sender=None)

    assert OrganizationType.objects.count() == 5
    hotel = OrganizationType.objects.get(value='hotel')
    assert hotel.old_id == '1'


@pytest.mark.django_db
@patch("master.signals.insert_locationable_types")
@patch("master.signals.insert_company_types")
@patch("master.signals.insert_organization_types")
@patch("master.signals.insert_languages_and_currencies")
def test_insert_master_data_calls_all(mock_lang, mock_org, mock_comp, mock_loc):
    insert_master_data(sender=None)
    mock_lang.assert_called_once()
    mock_org.assert_called_once()
    mock_comp.assert_called_once()
    mock_loc.assert_called_once()


# -------------- NEGATIVE TEST CASES ---------------- #

@pytest.mark.django_db
def test_currency_insertion_handles_duplicate_ids():
    Currency.objects.get_or_create(id=19, defaults={'value': 'usd', 'old_id': '18'})
    insert_languages_and_currencies(sender=None)

    assert Currency.objects.count() == 22
    updated_currency = Currency.objects.get(id=19)
    assert updated_currency.value == 'usd'


@pytest.mark.django_db
def test_language_insertion_overwrites_existing_entry():
    Language.objects.get_or_create(id=6, defaults={'value': 'xx', 'old_id': '999'})
    insert_languages_and_currencies(sender=None)

    updated_lang = Language.objects.get(id=6)
    assert updated_lang.value == 'en'
    assert updated_lang.old_id == '5'




@pytest.mark.django_db
def test_insert_company_types_with_invalid_data(monkeypatch):
    def broken_company_types(*args, **kwargs):
        from master.models import CompanyType
        TYPES = [
            (1, 'corporation', '0'),
            (2,),  # corrupt tuple
        ]
        for pk, value, old_id in TYPES:
            CompanyType.objects.update_or_create(id=pk, defaults={'value': value, 'old_id': old_id})

    monkeypatch.setattr("master.signals.insert_company_types", broken_company_types)

    with pytest.raises(ValueError):
        broken_company_types(sender=None)


@pytest.mark.django_db
def test_insert_functions_are_idempotent():
    insert_master_data(sender=None)
    first_currency_count = Currency.objects.count()
    first_language_count = Language.objects.count()

    insert_master_data(sender=None)
    second_currency_count = Currency.objects.count()
    second_language_count = Language.objects.count()

    assert first_currency_count == second_currency_count == 22
    assert first_language_count == second_language_count == 28
