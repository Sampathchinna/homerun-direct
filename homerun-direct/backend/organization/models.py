from django.db import models
from master.models import (
    Language,
    Currency,
    PaymentProcessor,
    Location,
    SubscriptionPlan,
    CompanyType,
    OrganizationType
)
from django.conf import settings
from django.core.exceptions import ValidationError
from organization.cache_utils import update_cache
from elasticsearch import Elasticsearch
from django.db.models.signals import post_save
from django.dispatch import receiver
from redis import Redis
from elasticsearch import Elasticsearch
from core.models import BaseModel


class Organization(BaseModel):
    organization_name = models.CharField(max_length=100, null=True)
    subdomain = models.CharField(max_length=254, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    organization_type = models.ForeignKey(
        OrganizationType, on_delete=models.SET_NULL, null=True
    )
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    company_type = models.ForeignKey(CompanyType, on_delete=models.SET_NULL, null=True)
    payment_processor = models.ForeignKey(
        PaymentProcessor, on_delete=models.SET_NULL, null=True
    )
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True
    )
    terms_agreement = models.BooleanField(default=False,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    ######### Migration Only Starts
    confirmed=models.BooleanField(default=False)
    # Migration purpose revamp
    class StatusChoices(models.TextChoices):
        RED = 'red', 'Red'
        YELLOW = 'yellow', 'Yellow'
        GREEN = 'green', 'Green'
        PURPLE = 'purple', 'Purple'


    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.GREEN,
    )

    parent_id=models.IntegerField(null=True, blank= True) # Just for migration sanity
    is_organization_created = models.BooleanField(default=False, null=True)
    ######### Migration Only Ends
    is_payment_done = models.BooleanField(default=False, null=True)
    stripe_subscription_id = models.CharField(max_length=257, null=True, blank=True)

    def clean_organization_name(self):
        if self.organization_name:
            self.organization_name = self.organization_name.strip()
            if Organization.objects.exclude(pk=self.pk).filter(
                organization_name__iexact=self.organization_name
            ).exists():
                raise ValidationError({'organization_name': 'Must be unique (trimmed, case-insensitive)'})

    def clean_subdomain(self):
        if self.subdomain:
            self.subdomain = self.subdomain.strip()
            if Organization.objects.exclude(pk=self.pk).filter(
                subdomain__iexact=self.subdomain
            ).exists():
                raise ValidationError({'subdomain': 'Must be unique (trimmed, case-insensitive)'})

    def clean(self):
        self.clean_organization_name()
        self.clean_subdomain()
        if self.user and not self.is_payment_done:
            unpaid_org_exists = Organization.objects.filter(
                user=self.user, is_payment_done=False
            ).exclude(id=self.id).exists()
            if unpaid_org_exists:
                raise ValidationError("You can only have one organization without payment")

    def save(self, *args, **kwargs):
        self.full_clean()  # Will run clean_ and clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.organization_name or "Unnamed Organization"


class OrgConfig(BaseModel):
    organization = models.OneToOneField('Organization', on_delete=models.CASCADE,primary_key=True)
    tenant_domains = models.TextField(null=True, blank=True)
    pmc_messages_only = models.BooleanField(null=True, blank=True, default=True)
    verification_message_enabled = models.BooleanField(null=True, blank=True, default=False)
    verification_reminder_message_enabled = models.BooleanField(null=True, blank=True, default=False)
    inquiry_received_enabled = models.BooleanField(null=True, blank=True, default=False)
    after_booking_confirmed_enabled = models.BooleanField(null=True, blank=True, default=False)
    check_in_instructions_verified_enabled = models.BooleanField(null=True, blank=True, default=False)
    check_in_instructions_enabled = models.BooleanField(null=True, blank=True, default=False)
    welcome_to_stay_enabled = models.BooleanField(null=True, blank=True, default=False)
    how_was_stay_enabled = models.BooleanField(null=True, blank=True, default=False)
    pointcentral_seamless_token = models.CharField(max_length=251, null=True, blank=True)
    pointcentral_session_token = models.CharField(max_length=252, null=True, blank=True)
    global_date_format = models.IntegerField(null=True, blank=True, default=1)
    should_split_bookings = models.BooleanField(null=True, blank=True, default=False)
    add_on_images = models.BooleanField(null=True, blank=True, default=False)
    kaba_access_token = models.CharField(max_length=253, null=True, blank=True)
    kaba_site_name = models.CharField(max_length=254, null=True, blank=True)
    csa_insurance_fee_rate = models.CharField(max_length=250, null=True, blank=True)
    csa_insurance_key = models.CharField(max_length=257, null=True, blank=True)
    keydata_token = models.TextField(null=True, blank=True)
    keydata_token_exp = models.CharField(max_length=259, null=True, blank=True)
    is_keydata_registered = models.BooleanField(null=True, blank=True)
    keydata_pmid = models.CharField(max_length=260, null=True, blank=True)
    keydata_embed_code = models.TextField(null=True, blank=True)
    locked = models.BooleanField(null=True, blank=True, default=True)
    payment_processor = models.IntegerField(null=True, blank=True, default=1)
    rvshare_import_batch_id = models.CharField(max_length=262, null=True, blank=True)
    feature_tier = models.TextField(null=False, blank=False)  # default="freemium'::ant.organization_feature_tier" (manual check)
    annual_maintenance_fee_added_at = models.DateTimeField(null=True, blank=True)

#1 Brands
class Brand(BaseModel):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=255, null=True, blank=True)
    date_format = models.CharField(max_length=255, null=True, blank=True)
    default = models.BooleanField(null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    verify_image = models.CharField(max_length=255, null=True, blank=True)
    verify_image_description = models.TextField(null=True, blank=True)
    verify_signature = models.CharField(max_length=255, null=True, blank=True)
    settings = models.JSONField(null=True, blank=True)
    rate_inflator = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cms_version = models.CharField(max_length=255, null=True, blank=True)

#2 BrandFooters
class BrandFooters(BaseModel):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    scripts = models.TextField(null=True, blank=True)
    sections = models.JSONField(null=True, blank=True)
    credit_cards = models.JSONField(null=True, blank=True)
    intercom_id = models.CharField(max_length=255, null=True, blank=True)
    custom_html = models.TextField(null=True, blank=True)

#3 BrandHeaders
class BrandHeaders(BaseModel):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    meta_tags = models.JSONField(null=True, blank=True)
    custom_html = models.TextField(null=True, blank=True)

#4 BrandHomePages
class BrandHomePages(BaseModel):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    template = models.IntegerField(null=True)
    payload = models.JSONField(null=True)
    options = models.TextField(max_length=256, null=True)
    meta_title = models.CharField(max_length=257, null=True)
    meta_description = models.CharField(max_length=258, null=True)
    cms_display_name = models.CharField(max_length=259, null=False)
    title = models.CharField(max_length=260, null=False)
    description = models.CharField(max_length=261, null=False)

#5 Brandinfos
class BrandInfos(BaseModel):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    theme = models.IntegerField(null=True, blank=True)
    colors = models.JSONField(null=True, blank=True)
    contact = models.JSONField(null=True, blank=True)
    css_override = models.TextField(null=True, blank=True)
    fonts = models.JSONField(null=True, blank=True)
    social = models.JSONField(null=True, blank=True)
    google_analytics = models.CharField(max_length=255, null=True, blank=True)
    logo_image = models.CharField(max_length=255, null=True, blank=True)
    logo_image_processing = models.BooleanField(null=True, blank=True)
    favicon_image = models.CharField(max_length=255, null=True, blank=True)
    favicon_image_processing = models.BooleanField(null=True, blank=True)
    copyright = models.TextField(null=True, blank=True)
    from_email = models.CharField(max_length=255, null=True, blank=True)
    signature = models.TextField(null=True)
    robots = models.CharField(max_length=2048, null=True)
    robots_name = models.CharField(max_length=255, null=True)
    custom_hero_html = models.TextField(null=True)
    scripts_override = models.TextField(null=True)
    bootstrap4 = models.BooleanField(null=True)
    body_class = models.CharField(max_length=255, null=True)
    google_tag_manager = models.CharField(max_length=255, null=True)
    facebook_pixel = models.CharField(max_length=255, null=True)
    hubspot_tracking = models.CharField(max_length=255, null=True)
    google_events = models.BooleanField(null=True)
    google_verification = models.CharField(max_length=255, null=True)
    legacy = models.BooleanField(null=True)
    logo_white_image = models.CharField(max_length=255, null=True, blank=True)
    logo_white_image_processing = models.BooleanField(null=False)
    book_now = models.JSONField(null=False)
    send_message = models.JSONField(null=False)

#6 BrandPages
class BrandPages(BaseModel):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    template = models.IntegerField(null=True)
    title = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    slug = models.CharField(max_length=255, null=True)
    payload = models.JSONField(null=True)
    featured = models.BooleanField(null=True)
    published = models.BooleanField(null=True)
    published_at = models.DateTimeField(null=True)
    contact_form = models.BooleanField(null=True)
    css_override = models.TextField(null=True)
    scripts_override = models.TextField(null=True)
    meta_title = models.CharField(max_length=255, null=True)
    meta_description = models.CharField(max_length=255, null=True)
    cms_display_name = models.CharField(max_length=255, null=True)

#7 BrandPageSliceHeadline
class BrandPageSliceHeadline(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    headline_text = models.CharField(max_length=255, null=True)
#8 BrandPageSliceAmenities
class BrandPageSliceAmenities(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    amenities_data = models.JSONField(null=True, blank=True)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True)

#9 BrandPageSliceFeaturedListings
class BrandPageSliceFeaturedListings(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True)
    listings_data = models.JSONField(null=True, blank=True)

#10 BrandPageSliceGridContentBlocks
class BrandPageSliceGridContentBlocks(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True, blank=True)
    column_data = models.JSONField(null=True, blank=True)
    number_of_columns = models.IntegerField(null=True, blank=True)

#11 BrandPageSliceHomepageHeros
class BrandPageSliceHomepageHeros(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True)
    bg_image = models.CharField(max_length=255, null=True)
    bg_image_gallery = models.JSONField(null=True)
    bg_video = models.CharField(max_length=255, null=True)
    bg_type = models.IntegerField(null=True)
    headline = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)
    layout_type = models.IntegerField(null=True)
#12 Brandpagesliceheros
class Brandpagesliceheros(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True)
    bg_image = models.CharField(max_length=255, null=True)
    bg_image_gallery = models.JSONField(null=True)
    bg_video = models.CharField(max_length=255, null=True)
    bg_type = models.IntegerField(null=True)
    headline = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)


#13 BrandPageSliceLocalActivities
class BrandPageSliceLocalActivities(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True)
    local_activities_data = models.JSONField(null=True, blank=True)

#14 BrandPageSliceMediaContentBlocks
class BrandPageSliceMediaContentBlocks(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True)
    bg_image = models.CharField(max_length=255, null=True)
    bg_image_gallery = models.JSONField(null=True)
    bg_video = models.CharField(max_length=255, null=True)
    bg_type = models.IntegerField(null=True)
    headline = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, null=True)

#15 BrandPageSliceMediaContentBlocks
class BrandPageSlicePhotoGalleries(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True)
    photo_gallery = models.JSONField(null=True)

#16 BrandPageSlicePullQuotes
class BrandPageSlicePullQuotes(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True)
    quote_text = models.CharField(max_length=255, null=True)
    quote_author = models.CharField(max_length=255, null=True)
    quote_author_image = models.CharField(max_length=255, null=True)

#17 BrandPageSliceReviews
class BrandPageSliceReviews(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True, blank=True)
    custom_name = models.CharField(max_length=255, null=True)
    review_data = models.JSONField(null=True, blank=True)

#18 BrandPageSliceSingleImages
class BrandPageSliceSingleImages(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True)
    image_url = models.CharField(max_length=255, null=True)
    width = models.IntegerField(null=True)
    justify = models.IntegerField(null=True)

#19 BrandPageSliceVideoEmbeds
class BrandPageSliceVideoEmbeds(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    page_sort = models.IntegerField(null=True)
    custom_name = models.CharField(max_length=255, null=True)
    video_url = models.CharField(max_length=255, null=True)
    video_source = models.IntegerField(null=True)
    width = models.CharField(max_length=255, null=True)
    justify = models.IntegerField(null=True)

#20 BrandPageSlices
class BrandPageSlices(BaseModel):
    brand_page = models.ForeignKey('BrandPages', on_delete=models.CASCADE)
    default_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True)
    slice_key = models.CharField(max_length=255, null=True, blank=True)




class BrandsEmployees(BaseModel):
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    ### $ TODO : This will be from Users, Type EMployye RBAC
    employee_id = models.BigIntegerField(null=False)
    all_id = models.BigIntegerField(null=True)


@receiver(post_save, sender=Location)
def update_organization_cache_on_location_change(sender, instance, **kwargs):
    """Update cache for all organizations linked to this location"""
    organizations = instance.organization_set.all()
    for org in organizations:
        update_cache(org)


