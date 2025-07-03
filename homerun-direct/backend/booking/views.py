from rest_framework.permissions import IsAuthenticated
from core.viewsets import GenericModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from core.pagination import CustomPagination
from .models import BookingNetDetails
from .serializers import BookingNetDetailsSerializer
class BookingNetDetailsViewSet(GenericModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter]
    pagination_class = CustomPagination
    queryset = BookingNetDetails.objects.all()
    serializer_class = BookingNetDetailsSerializer

from .models import Bookings
from .serializers import BookingsSerializer
class BookingsViewSet(GenericModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter]
    pagination_class = CustomPagination
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

from .models import BookingsFees
from .serializers import BookingsFeesSerializer
class BookingsFeesViewSet(GenericModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter]
    pagination_class = CustomPagination
    queryset = BookingsFees.objects.all()
    serializer_class = BookingsFeesSerializer

from .models import LineItems
from .serializers import LineItemsSerializer
class LineItemsViewSet(GenericModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter]
    pagination_class = CustomPagination
    queryset = LineItems.objects.all()
    serializer_class = LineItemsSerializer
