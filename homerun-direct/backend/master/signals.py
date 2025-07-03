
def insert_languages_and_currencies(sender, **kwargs):
    from master.models import Currency, Language

    # 💰 Currency seed data: (id, value, old_id)
    CURRENCIES = [
        (1, 'aud', '0'), (2, 'brl', '1'), (3, 'cad', '2'), (4, 'chf', '3'),
        (5, 'cny', '4'), (6, 'eur', '5'), (7, 'gbp', '6'), (8, 'hkd', '7'),
        (9, 'inr', '8'), (10, 'jpy', '9'), (11, 'krw', '10'), (12, 'mxn', '11'),
        (13, 'nok', '12'), (14, 'nzd', '13'), (15, 'rub', '14'), (16, 'sek', '15'),
        (17, 'sgd', '16'), (18, 'try', '17'), (19, 'usd', '18'), (20, 'zar', '19'),
        (21, 'clp', '20'), (22, 'thb', '21')
    ]

    # 🌐 Language seed data: (id, value, old_id)
    LANGUAGES = [
        (1, 'ar', '0'), (2, 'bn', '1'), (3, 'cs', '2'), (4, 'da', '3'),
        (5, 'nl', '4'), (6, 'en', '5'), (7, 'et', '6'), (8, 'fr', '7'),
        (9, 'de', '8'), (10, 'el', '9'), (11, 'hi', '10'), (12, 'hu', '11'),
        (13, 'id', '12'), (14, 'it', '13'), (15, 'ja', '14'), (16, 'jv', '15'),
        (17, 'ko', '16'), (18, 'nb', '17'), (19, 'pa', '18'), (20, 'pl', '19'),
        (21, 'pt', '20'), (22, 'ru', '21'), (23, 'es', '22'), (24, 'sv', '23'),
        (25, 'th', '24'), (26, 'tr', '25'), (27, 'vi', '26'), (28, 'zh', '27')
    ]

    for pk, value, old_id in CURRENCIES:
        Currency.objects.update_or_create(id=pk, defaults={"value": value, "old_id": old_id})

    for pk, value, old_id in LANGUAGES:
        Language.objects.update_or_create(id=pk, defaults={"value": value, "old_id": old_id})

def insert_locationable_types(sender, **kwargs):
    from master.models import LocationableType

    TYPES = [
        (1, 'Organization'),
        (2, 'Property'),
        (3, 'Customer'),
        (4, 'Employee'),
        (5, 'Vehicle'),
        (6, 'DeliveryLocation'),
        (7, 'Team'),
        (8, 'Brand'),
        (9, 'NA'), # For null values from legacy system around 50 such recs

    ]

    for id_val, name in TYPES:
        LocationableType.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_company_types(sender, **kwargs):
    from master.models import CompanyType

    TYPES = [
        (1, 'corporation', '0'),
        (2, 'sole_prop', '1'),
        (3, 'non_profit', '2'),
        (4, 'partnership', '3'),
        (5, 'llc', '4'),
        (6, 'other', '5'),
    ]

    for pk, value, old_id in TYPES:
        CompanyType.objects.update_or_create(
            id=pk,
            defaults={'value': value, 'old_id': old_id}
        )

def insert_organization_types(sender, **kwargs):
    from master.models import OrganizationType

    TYPES = [
        (1, 'bnb', '0'),
        (2, 'hotel', '1'),
        (3, 'hostel', '2'),
        (4, 'vacation_rental', '3'),
        (5, 'rv_fleet', '4')
    ]

    for pk, value, old_id in TYPES:
        OrganizationType.objects.update_or_create(
            id=pk,
            defaults={'value': value, 'old_id': old_id}
        )


def insert_property_types(sender, **kwargs):
    from master.models import PropertyType

    TYPES = [
        (1, 'apartment', '0'),
        (2, 'apartment_building', '1'),
        (3, 'barn', '2'),
        (4, 'boat', '3'),
        (5, 'bnb', '4'),
        (6, 'bnb_unit', '5'),
        (7, 'building', '6'),
        (8, 'bungalow', '7'),
        (9, 'cabin', '8'),
        (10, 'caravan', '9'),
        (11, 'castle', '10'),
        (12, 'chacara', '11'),
        (13, 'chalet', '12'),
        (14, 'chateau', '13'),
        (15, 'condo', '14'),
        (16, 'condo_building', '15'),
        (17, 'condo_hotel', '16'),
        (18, 'condo_hotel_unit', '17'),
        (19, 'cottage', '18'),
        (20, 'estate', '19'),
        (21, 'farmhouse', '20'),
        (22, 'guesthouse', '21'),
        (23, 'hotel', '22'),
        (24, 'hotel_unit', '23'),
        (25, 'house', '24'),
        (26, 'house_boat', '25'),
        (27, 'lodge', '26'),
        (28, 'mas', '27'),
        (29, 'mill', '28'),
        (30, 'mobile_home', '29'),
        (31, 'recreational_vehicle', '30'),
        (32, 'vehicle', '31'),
        (33, 'riad', '32'),
        (34, 'studio', '33'),
        (35, 'tower', '34'),
        (36, 'townhome', '35'),
        (37, 'villa', '36'),
        (38, 'yacht', '37'),
        (99, 'N/A', None),

    ]

    for pk, value, old_id in TYPES:
        PropertyType.objects.update_or_create(
            id=pk,
            defaults={'value': value, 'old_id': old_id}
        )
def insert_master_data(sender, **kwargs):
    insert_locationable_types(sender, **kwargs)
    insert_company_types(sender, **kwargs)
    insert_organization_types(sender, **kwargs)
    insert_languages_and_currencies(sender, **kwargs)
    insert_property_types(sender, **kwargs)

    

