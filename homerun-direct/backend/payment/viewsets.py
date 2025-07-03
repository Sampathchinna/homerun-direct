import stripe
from rest_framework.views import APIView
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from payment.services.stripe_utils import process_stripe_webhook
from rest_framework.permissions import AllowAny

class StripeSessionDetailView(APIView):
    def get(self, request, session_id):
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return JsonResponse({"session": session}, status=200)
        except stripe.error.InvalidRequestError:
            return JsonResponse({"error": "Invalid session ID"}, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]  # No authentication required for Stripe webhooks

    def post(self, request, *args, **kwargs):
        """Handles Stripe webhook events."""
        return process_stripe_webhook(request.body, request.META.get("HTTP_STRIPE_SIGNATURE"))
