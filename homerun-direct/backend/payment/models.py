from django.db import models
from core.models import BaseModel
from organization.models import Organization
from django.conf import settings
# Create your models here.
class StripeCustomer(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stripe_profiles",
    )
    organization = models.OneToOneField(
        "organization.Organization", on_delete=models.CASCADE, related_name="stripe_data"
    )
    # Stripe identifiers
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_method_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_price_id = models.CharField(
        max_length=255, blank=True, null=True
    )  # Plan/price
    latest_invoice_url = models.URLField(blank=True, null=True)

    subscription_status = models.CharField(
        max_length=50,
        choices=[
            ("active", "Active"),
            ("past_due", "Past Due"),
            ("canceled", "Canceled"),
            ("incomplete", "Incomplete"),
            ("trialing", "Trialing"),
        ],
        default="incomplete",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
