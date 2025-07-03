import pytest
from rest_framework.test import APIClient
from unittest.mock import patch
from rest_framework.response import Response
from stripe.error import InvalidRequestError

# ✅ Positive Test: StripeSessionDetailView
@pytest.mark.django_db
@patch("stripe.checkout.Session.retrieve")
def test_get_stripe_session_success(mock_retrieve):
    client = APIClient()
    session_id = "sess_123"

    mock_retrieve.return_value = {"id": session_id, "status": "complete"}

    response = client.get(f"/api/payment/stripe-session/{session_id}/")

    assert response.status_code == 200
    assert response.json()["session"]["id"] == session_id

# ❌ Negative Test: StripeSessionDetailView with Invalid Session ID
@pytest.mark.django_db
@patch("stripe.checkout.Session.retrieve")
def test_get_stripe_session_invalid_id(mock_retrieve):
    client = APIClient()
    session_id = "invalid_session"

    mock_retrieve.side_effect = InvalidRequestError("Invalid session", "session_id")

    response = client.get(f"/api/payment/stripe-session/{session_id}/")

    assert response.status_code == 400
    assert response.json() == {"error": "Invalid session ID"}

# ✅ Positive Test: StripeWebhookView with valid signature
@patch("payment.viewsets.process_stripe_webhook")
def test_stripe_webhook_success(mock_process_webhook):
    client = APIClient()
    mock_process_webhook.return_value = Response({"status": "success"}, status=200)

    body = b'{"id": "evt_test"}'
    signature = "test_signature"

    response = client.post(
        "/api/payment/stripe-webhook/",
        data=body,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=signature
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    mock_process_webhook.assert_called_once_with(body, signature)

# ❌ Negative Test: StripeWebhookView missing signature
@patch("payment.viewsets.process_stripe_webhook")
def test_stripe_webhook_missing_signature(mock_process_webhook):
    client = APIClient()
    mock_process_webhook.return_value = Response({"error": "Signature missing"}, status=400)

    body = b'{"id": "evt_test"}'

    response = client.post(
        "/api/payment/stripe-webhook/",
        data=body,
        content_type="application/json"
        # Missing HTTP_STRIPE_SIGNATURE
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Signature missing"
    mock_process_webhook.assert_called_once_with(body, None)
