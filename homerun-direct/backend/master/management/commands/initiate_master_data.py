from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from master.models import (
    PaymentProcessor,
    SubscriptionPlan,
)
from core.models import Entity


class Command(BaseCommand):
    help = "Seeds master data like company types, languages, currencies, payment processors, etc."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting master data seeding...")

        
        # Payment Processors
        PaymentProcessor.objects.all().delete()
        payment_processors = [
            (1, "Lynnbrook", "lynnbrook"),
            (2, "Stripe", "stripe"),
            (3, "Undecided - Will Select Later", "undecided-will-select-later"),
        ]
        for id_, label, value in payment_processors:
            PaymentProcessor.objects.update_or_create(
                id=id_, defaults={"label": label, "value": value}
            )
        stripe_processor = PaymentProcessor.objects.get(value="stripe")
        lynbrook_processor = PaymentProcessor.objects.get(value="lynnbrook")

        # Step 3: Create or update subscription plans
        plans = [
            {
                "name": "Basic Plan",
                "interval": "month",
                "price_cents": 100,
                "provider": stripe_processor,
            },
            {
                "name": "Premium Plan",
                "interval": "year",
                "price_cents": 100,
                "provider": stripe_processor,
            },
            {
                "name": "Basic Plan",
                "interval": "month",
                "price_cents": 120,
                "provider": lynbrook_processor,
            },
            {
                "name": "Premium Plan",
                "interval": "year",
                "price_cents": 110,
                "provider": lynbrook_processor,
            },
        ]

        for plan in plans:
            obj, created = SubscriptionPlan.objects.update_or_create(
                name=plan["name"],
                interval=plan["interval"],
                provider=plan["provider"],
                defaults={"price_cents": plan["price_cents"]},
            )
            status = "Created" if created else "Updated"
        # Currencies
        
        self.stdout.write(
            self.style.SUCCESS("✅ Master data initialized successfully!")
        )
        # Create superuser if not exists
        
        

        # Create one Entity record
        Entity.objects.update_or_create(
            url_path="/api/organization/",
            defaults={
                "name": "Org",
                "model_path": "organization.Organization",
                "form": {"className": "grid md:grid-cols-4 grid-cols-1 gap-4"},
                "post_heading": {
                    "type": "heading_dynamic",
                    "headingType": "h2",
                    "label": "Let's Get Started",
                    "tab": "setup_organizations",
                },
                "post_description": {
                    "type": "description",
                    "description": "Setting up your Organization will be quick and easy. Start by telling us a few basics about your Organization.",
                    "tab": "setup_organizations",
                },
                "extra_parameter": {
                    "terms_agreement": {
                        "label": "I have read and agree to the Manager License Agreement and {terms_of_service} and {privacy_policy}.",
                        "required": True,
                        "label_hidden": True,
                        "column_class_name": "md:col-span-4",
                        "options": {
                            "terms_of_service": {
                                "label": "Terms of service",
                                "link": "/#",
                                "target": "_blank",
                            },
                            "privacy_policy": {
                                "label": "Privacy Policy",
                                "link": "/#",
                                "target": "_blank",
                            },
                        },
                    },
                    "organization_name": {"column_class_name": "md:col-span-4"},
                    "organization_type": {"column_class_name": "md:col-span-4"},
                    "company_type": {"column_class_name": "md:col-span-4"},
                    "language": {"column_class_name": "md:col-span-4"},
                    "currency": {"column_class_name": "md:col-span-4"},
                    "payment_processor": {"column_class_name": "md:col-span-4"},
                    "heading": {"column_class_name": "md:col-span-4"},
                    "description": {"column_class_name": "md:col-span-4"},
                },
                "extra_field": {
                    "street_address": {
                        "type": "google_address",
                        "read_only": False,
                        "label": "Street Address",
                        "address_config": {
                            "isStandalone": False,
                            "autoPopulate": {
                                "state": "state_province",
                                "city": "city",
                                "zip_code": "postal_code",
                                "country": "country",
                                "latitude": "latitude",
                                "longitude": "longitude",
                            },
                        },
                        "tab": "business_location",
                        "required": True,
                        "max_length": 100,
                        "placeholder": "",
                        "column_class_name": "md:col-span-3",
                    },
                    "apt_suite": {
                        "type": "string",
                        "read_only": False,
                        "label": "Apt/Suite",
                        "tab": "business_location",
                        "required": False,
                        "max_length": 100,
                        "placeholder": "",
                        "column_class_name": "",
                    },
                    "city": {
                        "type": "string",
                        "read_only": False,
                        "label": "City",
                        "tab": "business_location",
                        "required": True,
                        "max_length": 100,
                        "placeholder": "",
                        "column_class_name": "md:col-span-2",
                    },
                    "state_province": {
                        "type": "string",
                        "read_only": False,
                        "label": "State/Province",
                        "tab": "business_location",
                        "required": True,
                        "max_length": 100,
                        "placeholder": "",
                        "column_class_name": "",
                    },
                    "postal_code": {
                        "type": "string",
                        "read_only": False,
                        "label": "Postal Code",
                        "tab": "business_location",
                        "required": True,
                        "max_length": 100,
                        "placeholder": "",
                        "column_class_name": "",
                    },
                    "country": {
                        "type": "string",
                        "read_only": False,
                        "label": "Country",
                        "tab": "business_location",
                        "required": True,
                        "max_length": 100,
                        "placeholder": "",
                        "column_class_name": "md:col-span-4",
                    },
                    "latitude": {
                        "type": "hidden",
                        "read_only": False,
                        "label": "Latitude",
                        "tab": "business_location",
                        "required": False,
                        "max_length": 100,
                        "placeholder": "",
                        "label_hidden": True,
                        "column_class_name": "md:col-span-4",
                    },
                    "longitude": {
                        "type": "hidden",
                        "read_only": False,
                        "label": "Longitude",
                        "tab": "business_location",
                        "required": False,
                        "max_length": 100,
                        "placeholder": "",
                        "label_hidden": True,
                        "column_class_name": "md:col-span-4",
                    },
                },
                "post_tabs": {
                    "setup_organizations": [
                        "organization_name",
                        "organization_type",
                        "language",
                        "currency",
                        "payment_processor",
                        "company_type",
                        "heading",
                    ],
                    "business_location": [
                        "street_address",
                        "apt_suite",
                        "city",
                        "state_province",
                        "postal_code",
                        "country",
                    ],
                    "terms_of_service": ["terms_agreement"],
                },
                "post_order": [
                    "heading",
                    "description",
                    {
                        "type": "heading_dynamic",
                        "headingType": "h3",
                        "label": "Organization Details",
                        "tab": "setup_organizations",
                        "column_class_name": "col-span-4",
                    },
                    "organization_name",
                    "organization_type",
                    {
                        "type": "heading_dynamic",
                        "headingType": "h3",
                        "label": "Business Details",
                        "tab": "setup_organizations",
                        "column_class_name": "col-span-4",
                    },
                    "company_type",
                    "language",
                    "currency",
                    "payment_processor",
                    {
                        "type": "heading_dynamic",
                        "headingType": "h2",
                        "label": "Business Location",
                        "tab": "business_location",
                        "column_class_name": "col-span-4",
                    },
                    {
                        "type": "description",
                        "description": "Please provide your business’s physical address",
                        "tab": "business_location",
                        "column_class_name": "col-span-4",
                    },
                    "street_address",
                    "apt_suite",
                    "city",
                    "state_province",
                    "postal_code",
                    "country",
                    "subscription_plan",
                    "terms_agreement",
                    "created_at",
                    "user",
                    "is_organization_created",
                ],
            },
        )

        self.stdout.write(self.style.SUCCESS("📦 Entity created/updated: Org"))
User = get_user_model()
User.objects.create_superuser(
    username="nishu",  
    password="nishu"
)
