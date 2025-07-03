from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .viewsets import *

router = DefaultRouter()

# # Register all the viewsets with the router
router.register(r'api/booking', BookingViewSet, basename='booking')


urlpatterns = [
    path("", include(router.urls)),
]
