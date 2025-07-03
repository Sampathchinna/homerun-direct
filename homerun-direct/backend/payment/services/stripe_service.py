import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from organization.models import Organization, SubscriptionPlan
from payment.models import StripeCustomer
from django.contrib.auth import get_user_model

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(user, subscription_plan_id, organization_id):
    subscription_plan = get_object_or_404(SubscriptionPlan, id=subscription_plan_id)
    organization = get_object_or_404(Organization, id=organization_id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        customer_email=user.email,
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': subscription_plan.name},
                'unit_amount': subscription_plan.price_cents,
                'recurring': {'interval': subscription_plan.interval}
            },
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f'{settings.FRONTEND_URL}/payment-success/',
        cancel_url=f'{settings.FRONTEND_URL}/payment-cancelled/',
        metadata={"user_id": user.id, "subscription_plan_id": subscription_plan.id, "organization_id": organization.id}
    )
    return session
