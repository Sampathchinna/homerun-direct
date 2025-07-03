from django.db import models
from django.db.models import JSONField
from core.models import BaseModel
from master.models import Location, PropertyType
from organization.models import Organization,Brand
from django.core.exceptions import ValidationError

class Property(BaseModel):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=False)
    multi_unit = models.BooleanField(default=False)
    summary_accommodations = models.TextField(null=True, blank=True)
    summary_description = models.TextField(null=True, blank=True)
    summary_headline = models.TextField(null=True, blank=True)
    summary_rules = models.TextField(null=True, blank=True)
    features_adventure = JSONField(default=dict)
    features_attractions = JSONField(default=dict)
    features_car = JSONField(default=dict)
    features_leisure = JSONField(default=dict)
    features_local = JSONField(default=dict)
    features_location = JSONField(default=dict)
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)  
    manager_info_visible = models.BooleanField(default=False)
    registration_id = models.CharField(max_length=100, null=True, blank=True)
    external_id = models.CharField(max_length=100, null=True, blank=True)
    extra = JSONField(default=dict,blank=True, null=True)
    unit_code = models.CharField(max_length=100, null=True, blank=True)
    features_cleaning = JSONField(default=dict)
    summary_description_plain_text = models.TextField(null=True, blank=True)
    summary_rules_plain_text = models.TextField(null=True, blank=True)
    direct_ical_url = models.URLField(null=True, blank=True)
    active_on_airbnb = models.BooleanField(default=False)
    active_on_homeaway = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def clean(self):
        if not self.name or not self.name.strip():
            raise ValidationError({"name": "Property name cannot be blank."})
        if self.summary_description and len(self.summary_description) < 10:
            raise ValidationError({"summary_description": "Description should be at least 10 characters."})
        if self.unit_code and not self.unit_code.isalnum():
            raise ValidationError({"unit_code": "Unit code must be alphanumeric."})
    
    def __str__(self):
            return self.name

class ImagesProperty(BaseModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    image = models.URLField()
    image_processing = models.BooleanField(default=False)
    label = models.CharField(max_length=255, blank=True)
    order = models.IntegerField(default=0)
    height = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def clean(self):
        if not self.image:
            raise ValidationError("Image URL is required.")
        if not self.organization:
            raise ValidationError("Organization must be assigned.")

class PropertyLocation(BaseModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)    


class GuestControls(BaseModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    children = JSONField(default=dict)
    smoking = JSONField(default=dict)
    #TODO Clean childer and smoking
    def clean(self):
        if not isinstance(self.children, dict):
            raise ValidationError("Field 'children' must be a dictionary.")



class InternetOptions(BaseModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)    
    is_internet_connection = models.BooleanField(default=False)
    homeaway_internet_cost = models.CharField(max_length=100, blank=True)
    homeaway_internet_speed = models.CharField(max_length=100, blank=True)
    wifi_username = models.CharField(max_length=100, blank=True)
    wifi_password = models.CharField(max_length=100, blank=True)

    def clean(self):
        if self.homeaway_internet_cost and not self.homeaway_internet_cost.replace('.', '', 1).isdigit():
            raise ValidationError({"homeaway_internet_cost": "Internet cost must be numeric."})
        if self.homeaway_internet_speed and not self.homeaway_internet_speed.replace('.', '', 1).isdigit():
            raise ValidationError({"homeaway_internet_speed": "Internet speed must be numeric."})



class LynnbrookAccount(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, related_name='lynnbrook_accounts', null=True, blank=True)
    target_id = models.IntegerField(null=True, blank=True)
    funding_type = models.IntegerField(null=True, blank=True)
    display_name = models.CharField(max_length=255, default='', blank=True)
    encrypted_checkbook_api_key = models.CharField(max_length=255, null=True, blank=True)
    encrypted_checkbook_api_secret = models.CharField(max_length=255, null=True, blank=True)
    checkbook_client_id = models.CharField(max_length=255, null=True, blank=True)
    encrypted_checkbook_api_key_iv = models.TextField(null=True, blank=True)
    encrypted_checkbook_api_secret_iv = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.display_name or f"Lynnbrook Account {self.id}"

class Portfolio(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    stripe_connect_account_id = models.IntegerField(null=True, blank=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True
    )

    lynnbrook_account = models.ForeignKey(
        LynnbrookAccount,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_index=True
    )

    def __str__(self):
        return self.name or f"Portfolio {self.id}"

class Subportfolio(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.DO_NOTHING, db_column='portfolio_id')  # FK
    organization_id = models.IntegerField(null=True, blank=True)  # Not a FK

    class Meta:
        db_table = 'subportfolios'

class RateGroup(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    subportfolio_id = models.BigIntegerField(null=True, blank=True)  # Not FK
    portfolio_id = models.BigIntegerField(null=True, blank=True)     # Not FK
    organization_id = models.IntegerField(null=True, blank=True)     # Not FK

    class Meta:
        db_table = 'rate_groups'


class UnitGroup(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    subportfolio_id = models.IntegerField(null=True, blank=True)  # Not FK
    rate_group_id = models.IntegerField(null=True, blank=True)    # Not FK
    portfolio_id = models.IntegerField(null=True, blank=True)     # Not FK
    start_date = models.CharField(max_length=255, null=True, blank=True)
    end_date = models.CharField(max_length=255, null=True, blank=True)
    default_nightly_weekday = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    default_nightly_weekend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_full_week = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_full_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  


class Vehicle(BaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True
    )
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.SET_NULL, null=True, blank=True
    )
    subportfolio = models.ForeignKey(
        Subportfolio, on_delete=models.SET_NULL, null=True, blank=True
    )
    unit_group = models.ForeignKey(
        UnitGroup, on_delete=models.SET_NULL, null=True, blank=True
    )
    rate_group = models.ForeignKey(
        RateGroup, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=False)
    vin_number = models.CharField(max_length=255, null=True, blank=True)
    show_manager_info = models.BooleanField(default=False)
    vehicle_type = models.IntegerField(null=True, blank=True)
    headline = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    transmission_type = models.IntegerField(null=True, blank=True)
    cruise_control = models.BooleanField(default=False)
    number_of_seatbelts = models.IntegerField(null=True, blank=True)
    fuel_type = models.IntegerField(null=True, blank=True)
    dual_battery = models.BooleanField(default=False)
    electric_service = models.IntegerField(null=True, blank=True)
    fuel_consumption = models.FloatField(null=True, blank=True)
    fuel_capacity = models.IntegerField(null=True, blank=True)
    gross_weight = models.FloatField(null=True, blank=True)
    dry_weight = models.FloatField(null=True, blank=True)
    cargo_weight = models.FloatField(null=True, blank=True)
    stationary = models.BooleanField(default=False)
    num_sleep_in_beds = models.IntegerField(null=True, blank=True)
    pets_allowed = models.BooleanField(null=True, blank=True)
    smoking_allowed = models.BooleanField(null=True, blank=True)
    wheelchair_accessible = models.BooleanField(null=True, blank=True)
    minimum_age_to_rent = models.IntegerField(default=25)
    electric_generator = models.BooleanField(default=False)
    navigation = models.BooleanField(default=False)
    kitchen_sink = models.BooleanField(default=False)
    rear_vision_camera = models.BooleanField(default=False)
    seat_belts = models.BooleanField(default=False)
    hot_and_cold_water_supply = models.BooleanField(default=False)
    slide_out = models.BooleanField(default=False)
    cd_player = models.BooleanField(default=False)
    dvd_player = models.BooleanField(default=False)
    games = models.BooleanField(default=False)
    satellite_cable_television = models.BooleanField(default=False)
    television = models.BooleanField(default=False)
    in_dash_air_conditioning = models.BooleanField(default=False)
    dryer = models.BooleanField(default=False)
    hair_dryer = models.BooleanField(default=False)
    heating = models.BooleanField(default=False)
    linens = models.BooleanField(default=False)
    towels = models.BooleanField(default=False)
    washer = models.BooleanField(default=False)
    essentials = models.BooleanField(default=False)
    dining_area = models.BooleanField(default=False)
    coffee_maker = models.BooleanField(default=False)
    utensils = models.BooleanField(default=False)
    dishwasher = models.BooleanField(default=False)
    microwave = models.BooleanField(default=False)
    oven = models.BooleanField(default=False)
    refrigerator = models.BooleanField(default=False)
    stove = models.BooleanField(default=False)
    toaster = models.BooleanField(default=False)
    first_aid_kit = models.BooleanField(default=False)
    fire_extinguisher = models.BooleanField(default=False)
    kayak_canoe = models.BooleanField(default=False)

    trailer_connector_type = models.CharField(max_length=255, null=True, blank=True)
    trailer_connector_adapter_provided = models.BooleanField(null=True, blank=True)
    hitch_provided = models.BooleanField(null=True, blank=True)
    anti_sway_device_provided = models.BooleanField(null=True, blank=True)
    trailer_ball_size = models.CharField(max_length=255, null=True, blank=True)
    engine = models.CharField(max_length=255, null=True, blank=True)
    power_steering = models.BooleanField(null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True)

    fresh_water_tank = models.FloatField(null=True, blank=True)
    shower = models.BooleanField(default=False)
    toilet = models.BooleanField(default=False)
    bathroom_sink = models.BooleanField(default=False)
    hitch_weight = models.FloatField(null=True, blank=True)
    length = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    slides = models.IntegerField(null=True, blank=True)

    stated_value = models.CharField(max_length=255, null=True, blank=True)
    stated_value_locked = models.BooleanField(default=False)

    roof_air_conditioning = models.BooleanField(default=False)
    ipod_docking_station = models.BooleanField(default=False)
    am_fm_radio = models.BooleanField(default=False)
    weight_distributing = models.BooleanField(null=True, blank=True)

    delivery_base_fee = models.CharField(max_length=255, null=True, blank=True)
    delivery_base_miles = models.CharField(max_length=255, null=True, blank=True)
    delivery_overage_rate = models.CharField(max_length=255, null=True, blank=True)
    delivery_overage_mile_limit = models.CharField(max_length=255, null=True, blank=True)
    delivery = models.BooleanField(default=False)

    stationary_description = models.CharField(max_length=255, default="", blank=True)
    delivery_base_id = models.CharField(max_length=255, null=True, blank=True)
    delivery_overage_id = models.CharField(max_length=255, null=True, blank=True)
    unit_code = models.CharField(max_length=255, null=True, blank=True)
    allow_sd_waiver = models.BooleanField(default=False)
    price_details = models.CharField(max_length=255, null=True, blank=True)
    description_plain_text = models.CharField(max_length=255, default="", blank=True)
    mba_insurance_policy_number = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return self.name or f"Vehicle {self.id}"

class ExternalContract(BaseModel):
    brand = models.ForeignKey(Brand, on_delete=models.DO_NOTHING, related_name="external_contracts", null=True, blank=True)
    organization_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, default='', blank=True)
    contact_emails = JSONField(default=list, blank=True)
    terms_and_conditions = models.TextField(default='', blank=True)
    e_sig_required = models.BooleanField(default=False)
    photo_id_required = models.BooleanField(default=False)
    address_required = models.BooleanField(default=False)
    age_required = models.BooleanField(default=False)
    required_age = models.IntegerField(default=18)
    photo_id_description = models.CharField(max_length=255, default='', blank=True)
    status = models.IntegerField(default=0)
    contract_body = models.TextField(default='', blank=True)

    def __str__(self):
        return self.name

class RoomType(models.Model):
    property = models.ForeignKey(Property, on_delete=models.DO_NOTHING, related_name='room_types', null=True, blank=True)
    calendar_id = models.BigIntegerField(null=True, blank=True)
    name = models.CharField(max_length=255)
    bedroom_count = models.FloatField(null=True, blank=True)
    bathroom_count = models.FloatField(null=True, blank=True)
    guest_count = models.IntegerField(null=True, blank=True)
    bed_config = models.TextField(null=True, blank=True)
    category = models.IntegerField(null=True, blank=True)
    default_availability_changeover = models.CharField(max_length=255, null=True, blank=True)
    default_stay_max = models.IntegerField(null=True, blank=True)
    default_stay_min = models.IntegerField(null=True, blank=True)
    default_time_check_in = models.CharField(max_length=255, null=True, blank=True)
    default_time_check_out = models.CharField(max_length=255, null=True, blank=True)
    default_prior_notify_min = models.IntegerField(null=True, blank=True)
    default_nightly_weekday = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    default_nightly_weekend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_full_week = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_full_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    organization_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Units(BaseModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(null=True, blank=True)

    summary_description = models.TextField(null=True, blank=True)
    summary_description_plain_text = models.TextField(null=True, blank=True)

    features_accommodations = models.TextField(null=True, blank=True)
    features_amenities = models.TextField(null=True, blank=True)
    features_dining = models.TextField(null=True, blank=True)
    features_entertainment = models.TextField(null=True, blank=True)
    features_outdoor = models.TextField(null=True, blank=True)
    features_spa = models.TextField(null=True, blank=True)
    features_suitability = models.TextField(null=True, blank=True)
    features_themes = models.TextField(null=True, blank=True)
    features_safety = models.TextField(null=True, blank=True)

    num_bathrooms = models.FloatField(null=True, blank=True)
    num_bedrooms = models.IntegerField(null=True, blank=True)
    num_lounge = models.IntegerField(null=True, blank=True)
    num_sleep = models.IntegerField(null=True, blank=True)
    num_sleep_in_beds = models.IntegerField(null=True, blank=True)
    num_parking_space = models.IntegerField(null=True, blank=True)

    unit_type = models.IntegerField(null=True, blank=True)
    measurement_type = models.IntegerField(default=0)
    size = models.IntegerField(null=True, blank=True)
    minimum_age = models.IntegerField(null=True, blank=True)

    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    organization_id = models.IntegerField(null=True, blank=True)
    unit_group_id = models.BigIntegerField(null=True, blank=True)
    rate_group_id = models.BigIntegerField(null=True, blank=True)


    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.DO_NOTHING,
        null=True, blank=True, db_index=True
    )
    subportfolio = models.ForeignKey(
        Subportfolio, on_delete=models.DO_NOTHING,
        null=True, blank=True, db_index=True
    )

    external_contract = models.ForeignKey(
        ExternalContract, on_delete=models.DO_NOTHING,
        null=True, blank=True, db_index=True
    )
    room_type = models.ForeignKey(
        RoomType, on_delete=models.DO_NOTHING,
        null=True, blank=True, db_index=True
    )

    external_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    pointcentral_customer_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    airbnb_headline = models.CharField(max_length=255, null=True, blank=True)
    bdc_headline = models.CharField(max_length=255, null=True, blank=True)
    airbnb_summary = models.CharField(max_length=255, null=True, blank=True)
    homeaway_internet_cost = models.CharField(max_length=255, null=True, blank=True)
    homeaway_internet_speed = models.IntegerField(null=True, blank=True)

    emergency_contact_phone = models.CharField(max_length=255, null=True, blank=True)
    emergency_contact_first_name = models.CharField(max_length=255, null=True, blank=True)
    emergency_contact_last_name = models.CharField(max_length=255, null=True, blank=True)

    guest_controls_description = models.CharField(max_length=255, null=True, blank=True)
    unit_code = models.CharField(max_length=255, null=True, blank=True)
    wifi_username = models.CharField(max_length=255, null=True, blank=True)
    wifi_password = models.CharField(max_length=255, null=True, blank=True)

    check_in_instructions = models.JSONField(default=dict, blank=True)
    extra = models.JSONField(default=dict, blank=True)

    enabled_on_kaba = models.BooleanField(default=False)
    

    class Meta:
        db_table = 'property_units'
        indexes = [
            models.Index(fields=['external_contract']),
            models.Index(fields=['portfolio']),
            models.Index(fields=['subportfolio']),
            models.Index(fields=['organization_id']),
            models.Index(fields=['external_id']),
            models.Index(fields=['pointcentral_customer_id']),
            models.Index(fields=['property_id']),
            models.Index(fields=['rate_group_id']),
            models.Index(fields=['room_type']),
            models.Index(fields=['unit_group_id']),
        ]

    def __str__(self):
        return self.name or f"Unit {self.id}"
    
    def clean(self):
        if self.num_sleep_in_beds is not None and self.num_sleep_in_beds < 0:
            raise ValidationError("Number of sleep-in beds must be 0 or more.")
        if self.num_bedrooms is not None and self.num_bedrooms < 0:
            raise ValidationError("Number of bedrooms must be 0 or more.")
        if self.num_bathrooms is not None and self.num_bathrooms < 0:
            raise ValidationError("Number of bathrooms must be 0 or more.")
        if self.num_lounge is not None and self.num_lounge < 0:
            raise ValidationError("Number of lounges must be 0 or more.")
        if self.num_parking_space is not None and self.num_parking_space < 0:
            raise ValidationError("Number of parking spaces must be 0 or more.")


class UnitListing(models.Model):
    currency = models.CharField(max_length=10, default='usd', blank=True, null=True)
    unit_id = models.BigIntegerField(null=True, blank=True)
    tax_rate = models.FloatField(null=True, blank=True)
    
    brand = models.ForeignKey(
        'organization.Brand', on_delete=models.DO_NOTHING, null=True, blank=True
    )
    
    instant_booking = models.BooleanField(null=True, blank=True)
    refund_policy = models.IntegerField(null=True, blank=True)
    refund_policy_custom = models.TextField(null=True, blank=True)
    featured = models.BooleanField(null=True, blank=True)

    enabled_distribution_homeaway = models.BooleanField(default=False)
    enabled_distribution_booking = models.BooleanField(default=False)
    enabled_distribution_airbnb = models.BooleanField(default=False)

    airbnb_refund_policy = models.IntegerField(null=True, blank=True)
    booking_dot_com_refund_policy = models.IntegerField(null=True, blank=True)
    homeaway_refund_policy = models.IntegerField(null=True, blank=True)

    adj_tax = models.FloatField(default=0.0)
    max_night_with_tax_rate = models.IntegerField(default=0)
    exclude_tax = models.BooleanField(default=False)
    tax_adjustable = models.BooleanField(default=False)

    organization_id = models.IntegerField(null=True, blank=True)  # Add FK if table available
    slug = models.CharField(max_length=255, null=True, blank=True)

    is_multi_unit = models.BooleanField(default=False)
    is_room_type = models.BooleanField(default=False)
    rate_inflator = models.FloatField(null=True, blank=True)

    primary = models.BooleanField(default=False)

    vehicle_id = models.BigIntegerField(null=True, blank=True)  # Add FK if `vehicle` model exists
    rvshare_cancellation_policy = models.IntegerField(null=True, blank=True)
    google_refund_policy = models.IntegerField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['brand'], name='idx_unitlist_brand_id'),
            models.Index(fields=['organization_id'], name='idx_unitlist_org_id'),
            models.Index(fields=['unit_id'], name='idx_unitlist_unit_id'),
            models.Index(fields=['vehicle_id'], name='idx_unitlist_vehicle_id'),
        ]

class UnitPricing(models.Model):
    default_nightly_weekday = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    default_nightly_weekend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_full_week = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    discount_full_month = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    pricing_calendar = models.JSONField(default=dict)

    unit = models.ForeignKey(Units, on_delete=models.DO_NOTHING, related_name='unit_pricings')
    unit_listing = models.ForeignKey(UnitListing, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)

    additional_guest_amount_cents = models.IntegerField(default=0)
    additional_guest_start = models.IntegerField(default=1)


    class Meta:
        indexes = [
            models.Index(fields=['organization']),
            models.Index(fields=['unit']),
            models.Index(fields=['unit_listing']),
            models.Index(fields=['vehicle']),
        ]

class BedroomsBathrooms(BaseModel):
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    num_of_bedrooms = models.IntegerField()
    num_sleep_in_beds = models.IntegerField()
    num_of_livingrooms = models.IntegerField()
    num_of_bathrooms = models.IntegerField()
    def clean(self):
        if self.num_of_bedrooms < 0:
            raise ValidationError("Number of bedrooms cannot be negative.")
        if self.num_of_bathrooms < 0:
            raise ValidationError("Number of bathrooms cannot be negative.")
        if self.num_of_livingrooms < 0:
            raise ValidationError("Number of living rooms cannot be negative.")
        if self.num_sleep_in_beds < 0:
            raise ValidationError("Number of beds cannot be negative.")


class Bedrooms(BaseModel):
    bedroom_type = models.CharField(max_length=50)
    amenities = JSONField(default=dict)
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    bedrooms_bathrooms = models.ForeignKey(BedroomsBathrooms, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    vehicle_id = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    # organization_id = models.IntegerField()

class LivingRooms(BaseModel):
    bedroom_type = models.CharField(max_length=50)
    amenities = JSONField(default=dict)
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    bedrooms_bathrooms = models.ForeignKey(BedroomsBathrooms, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    vehicle_id = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

class Bathroom(BaseModel):
    bathroom_type = models.CharField(max_length=50)
    amenities = JSONField(default=dict)
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    bedrooms_bathrooms = models.ForeignKey(BedroomsBathrooms, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

class Availability(BaseModel): #Unit
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    vehicle_id = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    default_availability_changeover = models.CharField(max_length=255, null=True, blank=True)
    default_stay_max = models.IntegerField(null=True, blank=True)
    default_stay_min = models.IntegerField(null=True, blank=True)
    default_time_check_in = models.CharField(max_length=255, default='12:00')
    default_time_check_out = models.CharField(max_length=255, default='12:00')
    default_prior_notify_min = models.IntegerField(null=True, blank=True)
    availability_calendar = models.JSONField(default=dict, blank=True)
    booking_calendar = models.JSONField(null=True, blank=True)
    check_in_check_out_policy = models.TextField(null=True, blank=True)  
    preparation_time = models.IntegerField(default=0)
    ical = models.CharField(max_length=255, null=True, blank=True)
    max_advance_res = models.IntegerField(null=True, blank=True)
    same_day_turnaround = models.BooleanField(default=True)

class Pricing(BaseModel):
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    default_nightly_weekday = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    default_nightly_weekend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_full_week = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    discount_full_month = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    pricing_calendar = models.JSONField(default=dict)
    # TODO unit_listing = models.ForeignKey(UnitListing, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    additional_guest_amount_cents = models.IntegerField(default=0)
    additional_guest_start = models.IntegerField(default=1)
    

    class Meta:
        db_table = 'unit_pricings'
        indexes = [
            models.Index(fields=['organization']),
            models.Index(fields=['unit']),
            #models.Index(fields=['unit_listing']),
            models.Index(fields=['vehicle']),
        ]

    def clean(self):
        if self.discount_full_week < 0 or self.discount_full_week >00:
            raise ValidationError("Weekly discount must be between 0 and 100.")
        if self.discount_full_month < 0 or self.discount_full_month > 100:
            raise ValidationError("Monthly discount must be between 0 and 100.")
        if self.default_nightly_weekday is not None and self.default_nightly_weekday < 0:
            raise ValidationError("Weekday rate cannot be negative.")
        if self.default_nightly_weekend is not None and self.default_nightly_weekend < 0:
            raise ValidationError("Weekend rate cannot be negative.")



class Deposits(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit_listing_id = models.IntegerField()
    calculation_type = models.CharField(max_length=50)
    calculation_amount = models.DecimalField(max_digits=8, decimal_places=2)
    refundable = models.BooleanField(default=False)
    taxable = models.BooleanField(default=False)
    remaining_balance_due_date = models.CharField(max_length=50)
    is_security_deposit = models.BooleanField(default=False)
    security_deposit_authorization = models.CharField(max_length=50)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    unit_pricing_id = models.IntegerField()
    auto_process_payments = models.BooleanField(default=False)

class FeeAccounts(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    refundable = models.BooleanField(default=False)
    taxable = models.BooleanField(default=False)
    optional = models.BooleanField(default=False)
    variable = models.BooleanField(default=False)
    included_in_base_rent = models.BooleanField(default=False)
    calculation_type = models.CharField(max_length=50)
    calculation_amount = models.DecimalField(max_digits=8, decimal_places=2)
    frequency = models.CharField(max_length=50)
    normalized_fee_name = models.CharField(max_length=100, null=True, blank=True)
    internal_use_only = models.BooleanField(default=False)
    realization_type = models.CharField(max_length=50)
    quantity_fee = models.BooleanField(default=False)
    fee_quantity_max = models.IntegerField(null=True, blank=True)
    split = models.CharField(max_length=50)
    cancellation = models.BooleanField(default=False)
    occurrence_date = models.CharField(max_length=50)
    debit_account_id = models.IntegerField()
    credit_account_id = models.IntegerField()
    active = models.BooleanField(default=True)
    los_ranges = JSONField(default=list)
    fee_count = models.IntegerField(default=0)
    fee_image = models.URLField(null=True, blank=True)
    owner_split = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def clean(self):
        if self.calculation_amount < 0:
            raise ValidationError({"calculation_amount": "Calculation amount must be non-negative."})
        if self.fee_quantity_max is not None and self.fee_quantity_max < 0:
            raise ValidationError({"fee_quantity_max": "Fee quantity max must be non-negative."})

class DebitAccount(BaseModel):
    name = models.CharField(max_length=100)

class CreditAccount(BaseModel):
    name = models.CharField(max_length=100)

class RefundPolicies(BaseModel):
    booking_dot_com_refund_policy = models.CharField(max_length=50)
    homeaway_refund_policy = models.CharField(max_length=50)
    airbnb_refund_policy = models.CharField(max_length=50)
    google_refund_policy = models.CharField(max_length=50)
    refund_policy_custom = models.CharField(max_length=50)


class ReservationNew(BaseModel):
    booking_range = JSONField()
    booking_type = models.CharField(max_length=50)
    check_in = models.DateField()
    check_out = models.DateField()
    confirmed = models.BooleanField(default=False)
    customer_id = models.IntegerField(null=True, blank=True)
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=255)
    customer_telephone = models.CharField(max_length=50)
    customer_addr_line_one = models.CharField(max_length=255, blank=True)
    customer_addr_line_two = models.CharField(max_length=255, blank=True)
    customer_city = models.CharField(max_length=100, blank=True)
    customer_state = models.CharField(max_length=100, blank=True)
    customer_country = models.CharField(max_length=100, blank=True)
    customer_zip = models.CharField(max_length=20, blank=True)
    listing_id = models.BigIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    channel_id = models.IntegerField(null=True, blank=True)
    send_confirmation = models.BooleanField(default=False)
    quote_id = models.BigIntegerField(null=True, blank=True)
    channel_fee_payable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    owner_will_self_clean = models.BooleanField(default=False)

    def clean(self):
        if self.check_out <= self.check_in:
            raise ValidationError("Check-out date must be after check-in date.")

class ReservationInformation(BaseModel):
    booking_range = JSONField()
    check_in = models.DateField()
    check_out = models.DateField()
    paid_status_override_flag = models.CharField(max_length=50)
    price_total = models.DecimalField(max_digits=10, decimal_places=2)
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()
    num_guests = models.IntegerField()

class FeeAccount(models.Model):
    organization_id = models.IntegerField(null=True, blank=True)  # Replace with ForeignKey if needed

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    refundable = models.BooleanField(default=True)
    taxable = models.BooleanField(default=True)
    optional = models.BooleanField(default=False)
    variable = models.BooleanField(default=False)
    included_in_base_rent = models.BooleanField(default=False)

    calculation_type = models.IntegerField(default=0)
    calculation_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    frequency = models.IntegerField(default=0)

    normalized_fee_name = models.CharField(max_length=255, null=True, blank=True)

    internal_use_only = models.BooleanField(default=False)
    realization_type = models.IntegerField(default=0)
    quantity_fee = models.BooleanField(default=False)
    fee_quantity_max = models.IntegerField(null=True, blank=True)

    split = models.CharField(max_length=255, default='no', null=True, blank=True)
    cancellation = models.BooleanField(default=False)
    occurrence_date = models.CharField(max_length=255, null=True, blank=True)

    debit_account_id = models.BigIntegerField(null=True, blank=True)
    credit_account_id = models.BigIntegerField(null=True, blank=True)

    active = models.BooleanField(default=True)


class OwnerSplit(models.Model):
    default = models.BooleanField()
    margin_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    margin_type = models.IntegerField(null=True, blank=True)

    organization_id = models.BigIntegerField(null=True, blank=True)  # Replace with ForeignKey if org model exists


    fee_account = models.ForeignKey(
        FeeAccount,  # Update path if FeeAccount is in a different app
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='owner_splits'
    )


class LineItemFee(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    total_cents = models.IntegerField(null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    taxable = models.BooleanField(default=False)
    item_type = models.CharField(max_length=255, null=True, blank=True)
    refundable = models.BooleanField(default=False)
    optional = models.BooleanField(default=False)
    additional_data = models.JSONField(default=dict, blank=True)

    organization_id = models.IntegerField(null=True, blank=True)  # replace with FK if model exists
    split = models.CharField(max_length=50, default='no')
    cancellation = models.BooleanField(default=False)
    occurrence_date = models.CharField(max_length=255, null=True, blank=True)

    debit_account_id = models.BigIntegerField(null=True, blank=True)  # replace with FK if needed
    credit_account_id = models.BigIntegerField(null=True, blank=True)

    # FK: owner_split
    owner_split = models.ForeignKey(
        OwnerSplit,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='line_items'
    )

class LineItemTax(LineItemFee):
    """Same fields as LineItemFee but separate endpoint"""
    class Meta:
        proxy = True

class PropertyListing(BaseModel):
    unit_listing_id = models.BigIntegerField()
    send_update_mailer = models.BooleanField(default=False)



class CustomerInformation(BaseModel):
    booking_id = models.ForeignKey(
        ReservationNew,  # Update path if FeeAccount is in a different app
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    email = models.EmailField()
    name = models.CharField(max_length=255)
    telephone = models.CharField(max_length=50)
    adr_street = models.CharField(max_length=255)
    adr_city = models.CharField(max_length=100)
    adr_state = models.CharField(max_length=100)
    adr_country = models.CharField(max_length=100)
    adr_zip = models.CharField(max_length=20)
    billing_adr_street = models.CharField(max_length=255)
    billing_adr_city = models.CharField(max_length=100)
    billing_adr_country = models.CharField(max_length=100)
    billing_adr_state = models.CharField(max_length=100)
    billing_adr_zip = models.CharField(max_length=20)

class Charge(BaseModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_code = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=255)
    customer_telephone = models.CharField(max_length=50)
    charge_type = models.CharField(max_length=50)
    note = models.TextField()
    no_receipt = models.BooleanField(default=False)
    post_date = models.DateTimeField()

class PaymentMethod(BaseModel):
    card_number = models.CharField(max_length=20)
    expires_on = models.CharField(max_length=10)
    card_name = models.CharField(max_length=255)
    zip = models.CharField(max_length=20)
    method_type = models.CharField(max_length=50)

class Note(BaseModel):
    booking_code = models.CharField(max_length=100)
    message = models.TextField()


class Quote(models.Model):
    unit = models.ForeignKey(Units, null=True, blank=True, on_delete=models.SET_NULL)
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True, on_delete=models.SET_NULL)

    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)

    room_rate_cents = models.IntegerField(default=0)
    fees_cents = models.IntegerField(default=0)
    taxes_cents = models.IntegerField(default=0)
    extras_cents = models.IntegerField(default=0)
    total_cents = models.IntegerField(default=0)

    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    subtotal_cents = models.IntegerField(default=0)
    direct_net_cents = models.IntegerField(default=0)
    billable_nights = models.IntegerField(default=0)

    tax_rate = models.FloatField(default=0.0)
    inflation_cents = models.IntegerField(default=0)
    inflation_rate = models.FloatField(default=0.0)
    discount_cents = models.IntegerField(default=0)
    deposit_cents = models.IntegerField(default=0)

    daily_rates = JSONField(default=list)
    booking_code = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=10, default='usd')

    channel_id = models.IntegerField(null=True, blank=True)
    num_guests = models.IntegerField(null=True, blank=True)
    organization_id = models.IntegerField(null=True, blank=True)  # Optional FK

    usage_data = JSONField(default=dict)

    class Meta:
        indexes = [
            models.Index(fields=['channel_id']),
            models.Index(fields=['organization_id']),
            models.Index(fields=['unit']),
            models.Index(fields=['vehicle']),
        ]


class Customer(models.Model):
    email = models.CharField(max_length=255, default='', blank=False)
    encrypted_password = models.CharField(max_length=255, default='')
    name = models.CharField(max_length=255, default='')
    avatar = models.CharField(max_length=255, default='', blank=True)
    avatar_processing = models.BooleanField(default=False)
    telephone = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    reset_password_token = models.CharField(max_length=255, null=True, blank=True, unique=True)
    reset_password_sent_at = models.DateTimeField(null=True, blank=True)
    remember_created_at = models.DateTimeField(null=True, blank=True)
    sign_in_count = models.IntegerField(default=0)
    current_sign_in_at = models.DateTimeField(null=True, blank=True)
    last_sign_in_at = models.DateTimeField(null=True, blank=True)
    current_sign_in_ip = models.GenericIPAddressField(null=True, blank=True)
    last_sign_in_ip = models.GenericIPAddressField(null=True, blank=True)
    provider = models.CharField(max_length=255, null=True, blank=True)
    uid = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    age_verified = models.BooleanField(default=False)
    tag = models.IntegerField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True)

    # Address fields
    adr_street = models.CharField(max_length=255, null=True, blank=True)
    adr_city = models.CharField(max_length=255, null=True, blank=True)
    adr_country = models.CharField(max_length=255, null=True, blank=True)
    adr_state = models.CharField(max_length=255, null=True, blank=True)
    adr_zip = models.CharField(max_length=255, null=True, blank=True)

    # Billing address
    billing_adr_street = models.CharField(max_length=255, null=True, blank=True)
    billing_adr_city = models.CharField(max_length=255, null=True, blank=True)
    billing_adr_country = models.CharField(max_length=255, null=True, blank=True)
    billing_adr_state = models.CharField(max_length=255, null=True, blank=True)
    billing_adr_zip = models.CharField(max_length=255, null=True, blank=True)

    external_id = models.CharField(max_length=255, null=True, blank=True)
    verified = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class DeliveryLocation(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.DO_NOTHING, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    google_place_id = models.CharField(max_length=255, null=True, blank=True)
    custom = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.name or f"Delivery Location {self.id}"

class Booking(BaseModel):
    booking_code = models.CharField(max_length=255, null=True, blank=True)
    archived = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    confirmed = models.BooleanField(null=True, blank=True)
    num_guests = models.IntegerField(null=True, blank=True)
    price_breakdown = models.CharField(max_length=255, null=True, blank=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    unit_listing = models.ForeignKey(UnitListing, null=True, blank=True, on_delete=models.SET_NULL)
    booking_range = models.CharField(max_length=255, null=True, blank=True)
    notes = models.CharField(max_length=255, default='[]')

    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    paid_status_override_flag = models.IntegerField(null=True, blank=True)
    channel_id = models.IntegerField(null=True, blank=True)  # Could be FK
    external_id = models.CharField(max_length=255, null=True, blank=True)

    charges_pending = models.BooleanField(default=False)
    type = models.CharField(max_length=255, null=True, blank=True)

    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    subtotal = models.IntegerField(null=True, blank=True)
    direct_fee = models.IntegerField(null=True, blank=True)
    org_total = models.IntegerField(null=True, blank=True)
    stripe_fee = models.IntegerField(null=True, blank=True)
    owner_total = models.IntegerField(null=True, blank=True)

    quote = models.ForeignKey(Quote, null=True, blank=True, on_delete=models.SET_NULL)
    stripe_transfers = JSONField(default=list)

    creation_method = models.IntegerField(default=0)
    booking_type = models.IntegerField(default=0)
    generated_as_type = models.IntegerField(null=True, blank=True)
    external_contract_code = models.CharField(max_length=255, null=True, blank=True)
    door_code = models.CharField(max_length=255, null=True, blank=True)

    organization_id = models.IntegerField(null=True, blank=True)  # Could be FK
    split_booking = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    channel_updatable = models.BooleanField(default=True)
    homeaway_cancellation_reservation_status = models.IntegerField(null=True, blank=True)
    owner_self_clean = models.BooleanField(default=False)
    invalid_card_enqued = models.DateField(null=True, blank=True)

    coupon_code = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    cancellation_reason = models.CharField(max_length=255, null=True, blank=True)
    cancellation_notes = models.CharField(max_length=255, null=True, blank=True)
    cancellation_date = models.DateField(null=True, blank=True)
    bdc_cancel_code = models.IntegerField(null=True, blank=True)
    airbnb_cancellation_policy = models.CharField(max_length=255, null=True, blank=True)
    connected_stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    awaiting_verification = models.BooleanField(default=False)
    alteration_request = models.DateField(null=True, blank=True)
    alteration_accepted = models.BooleanField(null=True, blank=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    rvshare_calendar_block_id = models.CharField(max_length=255, null=True, blank=True)
    balance_collection_date = models.DateField(null=True, blank=True)
    generator_usage_included = models.IntegerField(null=True, blank=True)
    mileage_included = models.IntegerField(null=True, blank=True)
    unlimited_generator = models.BooleanField(null=True, blank=True)
    rvshare_booking_cancellation_policy = models.IntegerField(null=True, blank=True)

    delivery_location = models.ForeignKey('DeliveryLocation', null=True, blank=True, on_delete=models.SET_NULL)
    payment_customer_id = models.CharField(max_length=255, null=True, blank=True)
    external_insurance_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'ant_bookings'
        indexes = [
            models.Index(fields=['booking_code']),
            models.Index(fields=['channel_id']),
            models.Index(fields=['check_in']),
            models.Index(fields=['check_out']),
            models.Index(fields=['customer']),
            models.Index(fields=['delivery_location']),
            models.Index(fields=['external_id']),
            models.Index(fields=['organization_id']),
            models.Index(fields=['quote']),
            models.Index(fields=['split_booking']),
            models.Index(fields=['stripe_customer_id']),
            models.Index(fields=['unit_listing']),
        ]

class WorkOrder(BaseModel):
    wo_type = models.IntegerField(null=True, blank=True)
    wo_source = models.IntegerField(null=True, blank=True)
    due_on = models.DateTimeField(null=True, blank=True)
    completed_on = models.DateTimeField(null=True, blank=True)
    paid_on = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    amount_cents = models.IntegerField(null=True, blank=True)
    assignee_type = models.CharField(max_length=255, null=True, blank=True)
    assignee_id = models.BigIntegerField(null=True, blank=True)

    unit = models.ForeignKey(
        Units,  # Replace with 'yourapp.Unit' if outside same app
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column='unit_id'
    )

    property = models.ForeignKey(
        Property,  # Replace with 'yourapp.Property'
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column='property_id'
    )

    booking = models.ForeignKey(
        Booking,  # Replace with 'yourapp.Booking'
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column='booking_id'
    )

    status = models.IntegerField(null=True, blank=True)
    organization_id = models.IntegerField(null=True, blank=True)
    job_type = models.CharField(max_length=255, null=True, blank=True)
    requester_id = models.BigIntegerField(null=True, blank=True)
    requester_type = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    task_types = models.JSONField(default=list, blank=True, null=True)
    job_started_at = models.CharField(max_length=255, null=True, blank=True)
    job_completed_at = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['assignee_type', 'assignee_id'], name='idx_wo_assignee'),
            models.Index(fields=['booking'], name='idx_wo_booking'),
            models.Index(fields=['organization_id'], name='idx_wo_org'),
            models.Index(fields=['property'], name='idx_wo_property'),
            models.Index(fields=['unit'], name='idx_wo_unit'),
        ]
    def __str__(self):
        return f"WO#{self.id} [{self.status}]"



class WorkReport(BaseModel):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, db_column='work_order_id')
    status = models.IntegerField()
    notes = JSONField(default=list,null=True, blank=True)
    base_amount_cents = models.IntegerField()
    total_adjustments_cents = models.IntegerField()
    total_cents = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    payment_terms = models.IntegerField()
    reporter_type = models.CharField(max_length=255, null=True, blank=True)
    reporter_id = models.BigIntegerField(null=True, blank=True)
    reviewer_type = models.CharField(max_length=255, null=True, blank=True)
    reviewer_id = models.BigIntegerField(null=True, blank=True)
    total_deductions_cents = models.IntegerField()
    organization_id = models.IntegerField(null=True, blank=True)
    job_started_at = models.DateTimeField(null=True, blank=True)
    job_completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['organization_id']),
            models.Index(fields=['reporter_type', 'reporter_id']),
            models.Index(fields=['reviewer_type', 'reviewer_id']),
            models.Index(fields=['work_order']),
        ]


class TaxAccounts(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    rate = models.FloatField()
    tax_type = models.IntegerField()
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    adj_tax = models.FloatField()
    max_night_with_tax_rate = models.IntegerField()
    exclude_tax = models.BooleanField(default=False)
    tax_adjustable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    applies_to_room_rate = models.BooleanField(default=True)
    occurrence_date = models.CharField(max_length=255)
    debit_account_id = models.BigIntegerField()
    credit_account_id = models.BigIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    


class DeductionAccounts(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='deduction_accounts')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    unit_listing_id = models.BigIntegerField()
    calculation_type = models.IntegerField(default=0)
    calculation_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    variable = models.BooleanField(default=False)
    frequency = models.IntegerField(default=0)
    realization_type = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    debit_account_id = models.BigIntegerField()
    credit_account_id = models.BigIntegerField()
    occurrence_date = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class InventoryItem(BaseModel):
    item_name = models.CharField(max_length=255)
    cost_cents = models.IntegerField()
    count = models.IntegerField()
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, related_name="inventory_items")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.item_name

class UsageAccount(BaseModel):
    usage_type = models.IntegerField()
    name = models.CharField(max_length=255)
    charge_type = models.IntegerField()
    amount_free = models.CharField(max_length=255)
    calculation_amount = models.FloatField()
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.name