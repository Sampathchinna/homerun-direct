from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework.routers import DefaultRouter
from payment.viewsets import StripeWebhookView,StripeSessionDetailView
from organization.viewsets import OrganizationViewSet

# ✅ Register router correctly

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("rbac.urls")),  # ✅ Include all RBAC-related routes
    path("", include("core.urls")),  # ✅ Include all RBAC-related routes
    path("", include("organization.urls")),  # ✅ Include all RBAC-related routes
    path("", include("property.urls")),
    path("", include("booking.urls")),
    path("api/stripe-webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("api/session/<str:session_id>/", StripeSessionDetailView.as_view(), name="stripe-session-detail"),
    path("api/payment/stripe-session/<str:session_id>/", StripeSessionDetailView.as_view(), name="stripe-session"),
    path("api/payment/stripe-webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]

