import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from organization.models import Organization, SubscriptionPlan
from payment.models import StripeCustomer
from django.contrib.auth import get_user_model

User = get_user_model()

def process_stripe_webhook(payload, sig_header):
    """
    Generic function to process Stripe webhooks.
    """
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Extract relevant data
    event_type = event["type"]
    event_data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        handle_checkout_completed(event_data)

    elif event_type == "invoice.payment_failed":
        handle_payment_failed(event_data)

    elif event_type == "customer.subscription.deleted":
        handle_subscription_canceled(event_data)

    elif event_type == "checkout.session.expired":
        handle_checkout_expired(event_data)

    return JsonResponse({"status": "success"})


def handle_checkout_completed(session):
    """
    Handle successful checkout session.
    """
    organization_id = session["metadata"].get("organization_id")
    subscription_plan_id = session["metadata"].get("subscription_plan_id")
    user_id = session["metadata"].get("user_id")

    stripe_customer_id = session.get("customer")
    stripe_subscription_id = session.get("subscription")

    organization = get_object_or_404(Organization, id=int(organization_id))
    subscription_plan = get_object_or_404(SubscriptionPlan, id=int(subscription_plan_id))
    user = get_object_or_404(User, id=int(user_id))

    organization.subscription_plan = subscription_plan
    organization.stripe_subscription_id = stripe_subscription_id
    organization.is_payment_done = True
    organization.save()

    # Fetch invoice URL
    invoice_url = None
    if session.get("invoice"):
        try:
            invoice = stripe.Invoice.retrieve(session["invoice"])
            invoice_url = invoice.get("hosted_invoice_url")
        except stripe.error.InvalidRequestError:
            invoice_url = None

    # Fetch price ID
    price_id = None
    try:
        line_items = stripe.checkout.Session.list_line_items(session["id"])
        if line_items["data"]:
            price_id = line_items["data"][0]["price"]["id"]
    except stripe.error.InvalidRequestError:
        price_id = None

    stripe_customer, created = StripeCustomer.objects.get_or_create(
        organization=organization,
        defaults={
            "user": user,
            "stripe_customer_id": stripe_customer_id,
            "stripe_subscription_id": stripe_subscription_id,
            "subscription_status": "active",
            "stripe_price_id": price_id,
            "latest_invoice_url": invoice_url,
            "stripe_payment_method_id": session.get("payment_intent"),
        }
    )

    if not created:
        stripe_customer.user=user
        stripe_customer.organization=organization
        stripe_customer.stripe_customer_id=stripe_customer_id
        stripe_customer.stripe_subscription_id = stripe_subscription_id
        stripe_customer.subscription_status = "active"
        stripe_customer.stripe_price_id = price_id
        stripe_customer.latest_invoice_url = invoice_url
        stripe_customer.stripe_payment_method_id = session.get("payment_intent")
        stripe_customer.save()


def handle_payment_failed(invoice):
    """
    Handle payment failure.
    """
    stripe_subscription_id = invoice.get("subscription")
    stripe_customer = StripeCustomer.objects.filter(stripe_subscription_id=stripe_subscription_id).first()

    if stripe_customer:
        stripe_customer.subscription_status = "failed"
        stripe_customer.save()


def handle_subscription_canceled(subscription):
    """
    Handle subscription cancellation.
    """
    stripe_subscription_id = subscription.get("id")
    stripe_customer = StripeCustomer.objects.filter(stripe_subscription_id=stripe_subscription_id).first()

    if stripe_customer:
        stripe_customer.subscription_status = "canceled"
        stripe_customer.save()


def handle_checkout_expired(session):
    """
    Handle checkout session expiration.
    """
    stripe_subscription_id = session.get("id")
    stripe_customer = StripeCustomer.objects.filter(stripe_subscription_id=stripe_subscription_id).first()

    if stripe_customer:
        stripe_customer.subscription_status = "canceled"
        stripe_customer.save()
