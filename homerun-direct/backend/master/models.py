from django.db import models
from core.models import BaseModel
class CurrencyChoices(models.TextChoices):
    AUD = 'aud', 'AUD'
    BRL = 'brl', 'BRL'
    CAD = 'cad', 'CAD'
    CHF = 'chf', 'CHF'
    CNY = 'cny', 'CNY'
    EUR = 'eur', 'EUR'
    GBP = 'gbp', 'GBP'
    HKD = 'hkd', 'HKD'
    INR = 'inr', 'INR'
    JPY = 'jpy', 'JPY'
    KRW = 'krw', 'KRW'
    MXN = 'mxn', 'MXN'
    NOK = 'nok', 'NOK'
    NZD = 'nzd', 'NZD'
    RUB = 'rub', 'RUB'
    SEK = 'sek', 'SEK'
    SGD = 'sgd', 'SGD'
    TRY = 'try', 'TRY'
    USD = 'usd', 'USD'
    ZAR = 'zar', 'ZAR'
    CLP = 'clp', 'CLP'
    THB = 'thb', 'THB'
class LanguageChoices(models.TextChoices):
    AR = 'ar', 'AR'
    BN = 'bn', 'BN'
    CS = 'cs', 'CS'
    DA = 'da', 'DA'
    NL = 'nl', 'NL'
    EN = 'en', 'EN'
    ET = 'et', 'ET'
    FR = 'fr', 'FR'
    DE = 'de', 'DE'
    EL = 'el', 'EL'
    HI = 'hi', 'HI'
    HU = 'hu', 'HU'
    ID = 'id', 'ID'
    IT = 'it', 'IT'
    JA = 'ja', 'JA'
    JV = 'jv', 'JV'
    KO = 'ko', 'KO'
    NB = 'nb', 'NB'
    PA = 'pa', 'PA'
    PL = 'pl', 'PL'
    PT = 'pt', 'PT'
    RU = 'ru', 'RU'
    ES = 'es', 'ES'
    SV = 'sv', 'SV'
    TH = 'th', 'TH'
    TR = 'tr', 'TR'
    VI = 'vi', 'VI'
    ZH = 'zh', 'ZH'

class PropertyType(models.Model):
    value = models.CharField(max_length=100)
    old_id = models.CharField(max_length=50, blank=True, null=True)

class Currency(models.Model):
    old_id = models.CharField(max_length=100)
    value = models.CharField(max_length=10, choices=CurrencyChoices.choices)

    def __str__(self):
        return self.value

class Language(models.Model):
    old_id = models.CharField(max_length=100)
    value = models.CharField(max_length=10, choices=LanguageChoices.choices)

    def __str__(self):
        return self.value

class OrganizationTypeChoices(models.TextChoices):
    BNB = 'bnb', 'Bnb'
    HOTEL = 'hotel', 'Hotel'
    HOSTEL = 'hostel', 'Hostel'
    VACATION_RENTAL = 'vacation_rental', 'Vacation Rental'
    RV_FLEET = 'rv_fleet', 'RV fleet'

class OrganizationType(BaseModel):
    old_id = models.CharField(max_length=100)
    value = models.CharField(
        max_length=100,
        choices=OrganizationTypeChoices.choices
    )
    def __str__(self):
        return self.value

class CompanyTypeChoices(models.TextChoices):
    CORPORATION = 'corporation', 'Corporation'
    SOLE_PROP = 'sole_prop', 'Sole Proprietorship'
    NON_PROFIT = 'non_profit', 'Non-Profit'
    PARTNERSHIP = 'partnership', 'Partnership'
    LLC = 'llc', 'LLC'
    OTHER = 'other', 'Other'

class CompanyType(models.Model):
    old_id = models.CharField(max_length=100)
    value = models.CharField(
        max_length=100,
        choices=CompanyTypeChoices.choices
    )

    def __str__(self):
        return self.get_value_display()
    

class PaymentProcessorType(models.TextChoices):
    STRIPE = "stripe", "Stripe"
    LYNBROOK = "lynbrook", "Lynnbrook"


class PaymentProcessor(models.Model):
    label = models.CharField(max_length=100)
    value = models.CharField(
        max_length=100,
        choices=PaymentProcessorType.choices,
        unique=True,  # Optional, if you want values to be unique
    )

    def __str__(self):
        return self.value

class LocationableType(models.Model):
    name = models.CharField(max_length=51, unique=True)

    def __str__(self):
        return self.name

class Location(BaseModel):
    apt_suite = models.CharField(max_length=100,blank=True, null=True)
    city = models.CharField(max_length=100, null=True)
    state_province = models.CharField(max_length=100, null=True)
    postal_code = models.CharField(max_length=20, null=True)
    country = models.CharField(max_length=100, null=True)
    street_address = models.CharField(max_length=255, null=True)
    latitude = models.DecimalField(
        max_digits=12, decimal_places=9, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=12, decimal_places=9, blank=True, null=True
    )
    exact = models.BooleanField(blank=True, null=True)
    timezone = models.CharField(max_length=53, blank=True, null=True)
    # TODO : After migration move to new table 
    # Just for migration purpose Not needed After Migration
    # E.g. Organization will have location id 
    # Also not locationable type is null as well , could have been used so mainitainng 
    locationable_type = models.ForeignKey(LocationableType, on_delete=models.CASCADE)
    # TODO coplete JSON from Google map is stored in new
    raw_json = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.city)

# Payment plans
class SubscriptionPlan(models.Model):
    INTERVAL_CHOICES = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    provider = models.ForeignKey(PaymentProcessor, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # E.g. "Organization Create Default", "Pro"
    interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES)
    price_cents = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.interval}) - {self.provider.value}"
