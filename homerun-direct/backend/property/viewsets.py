from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.mixin_es import ElasticSearchMixin
from core.mixin_redis import RedisCacheMixin
from core.viewsets import GenericModelViewSet
from core.pagination import CustomPagination
from .models import *
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rbac.org_level_permission import apply_organization_level_filter,apply_brand_level_filter
from rest_framework import filters
from core.mixin_es import es

# Common mixin for ES-backed viewsets
class ESModelViewSet(ElasticSearchMixin, GenericModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    pagination_class = CustomPagination
    redis_cache = RedisCacheMixin()

    def list(self, request, *args, **kwargs):
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 50))
        filters = request.query_params
        must_clauses = self.build_elasticsearch_filters(filters)
        # ✅ Allow filtering/search by organization_id (thanks to step 1 above)
        org_id = request.query_params.get("organization_id")
        if org_id:
            must_clauses.append({
                "term": {
                    "organization_id": org_id
                }
            })
        apply_organization_level_filter(request, must_clauses)

        # Optional search term
        search_query = request.query_params.get('search')
        if search_query and hasattr(self, 'search_fields'):
            must_clauses.append({
                'multi_match': {
                    'query': search_query,
                    'fields': self.search_fields,
                    'type': 'best_fields'
                }
            })

        query = {'query': {'bool': {'must': must_clauses}}}

        try:
            results = self.search_elasticsearch(
                index_name=self.index_name,
                query=query,
                page=page,
                per_page=per_page
            )
            return Response({
                'response': results,
                'pagination': {
                    'count': len(results),
                    'per_page': per_page,
                    'previous': None if page == 1 else page - 1,
                    'next': None if len(results) < per_page else page + 1
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print('⚠️ ES fallback:', e)
            return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        self.index_instance(instance, self.index_name)
        self.redis_cache.set_user_org_session(self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        self.index_instance(instance, self.index_name)
        self.redis_cache.set_user_org_session(self.request.user)

    def perform_destroy(self, instance):
        self.clear_index(instance, self.index_name)
        instance.delete()

    from core.mixin_es import es 
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            es_doc = self.es.get(index=self.index_name, id=pk)["_source"]
            return Response(es_doc)
        except Exception as e:
            print("🔥 ES retrieve failed. Falling back to DB:", e)
            return super().retrieve(request, *args, **kwargs)


class ReservationViewSet(ESModelViewSet):
    """
    CRUD for Reservations, with property_id/unit_id write-only fields handled in serializer.
    """
    queryset = ReservationNew.objects.all()
    serializer_class = ReservationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['booking_type', 'confirmed']
    search_fields = ['booking_type', 'price_status']
    ordering_fields = ['check_in', 'created_at']
    index_name = 'reservations'


class ReservationInformationViewSet(ESModelViewSet):
    queryset = ReservationInformation.objects.all()
    serializer_class = ReservationInformationSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['check_in', 'created_at']
    index_name = 'reservation_information'


class FeeLineItemViewSet(ESModelViewSet):
    queryset = LineItemFee.objects.all().order_by('-id')
    serializer_class = FeeLineItemSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['total_cents', 'id']
    index_name = 'fee_line_item'


class TaxLineItemViewSet(ESModelViewSet):
    queryset = LineItemTax.objects.all().order_by('-id')
    serializer_class = TaxLineItemSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['total_cents', 'id']
    index_name = 'tax_line_item'


class PropertyListingViewSet(ESModelViewSet):
    queryset = PropertyListing.objects.all().order_by('-id')
    serializer_class = PropertyListingSerializer
    index_name = 'property_listing'


class UnitListingViewSet(ESModelViewSet):
    queryset = UnitListing.objects.all().order_by('-id')
    serializer_class = UnitListingSerializer
    index_name = 'unit_listing'


class CustomerInformationViewSet(ESModelViewSet):
    queryset = CustomerInformation.objects.all().order_by('-id')
    serializer_class = CustomerInformationSerializer
    index_name = 'customer_information'


class ChargeViewSet(ESModelViewSet):
    queryset = Charge.objects.all().order_by('-post_date')
    serializer_class = ChargeSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['post_date', 'amount']
    index_name = 'charges'


class PaymentMethodViewSet(ESModelViewSet):
    queryset = PaymentMethod.objects.all().order_by('-id')
    serializer_class = PaymentMethodSerializer
    index_name = 'payment_method'


class NoteViewSet(ESModelViewSet):
    queryset = Note.objects.all().order_by('-id')
    serializer_class = NoteSerializer
    index_name = 'note'

class WorkOrderViewSet(ESModelViewSet):
    """
    CRUD for WorkOrders, with unit_id write-only field handled in serializer.
    """
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['wo_type', 'status', 'assignee_type']
    search_fields      = ['wo_type', 'friendlyStatus']
    ordering_fields    = ['due_on', 'created_at']
    index_name = 'work_order'


class WorkReportViewSet(ESModelViewSet):
    """
    A viewset for viewing and editing WorkReport instances.
    Supports CRUD operations for WorkReports and includes filtering, pagination, and validation.
    """
    queryset = WorkReport.objects.all()
    serializer_class = WorkReportSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['description', 'status']  # Example search fields
    ordering_fields = ['created_at', 'updated_at']  # Fields for ordering
    index_name = 'work_report'

    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle potential foreign key issues and respond with proper validation errors.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the WorkReport if valid
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Custom update method to handle validation and ensure valid foreign keys.
        """
        instance = self.get_object()  # Retrieve the existing WorkReport
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()  # Save after validation
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 1. InternetOptions
class InternetOptionsViewSet(ESModelViewSet):
    queryset = InternetOptions.objects.all()
    serializer_class = InternetOptionsSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'internet_options'

# 2. BedroomsBathrooms
class BedroomsBathroomsViewSet(ESModelViewSet):
    queryset = BedroomsBathrooms.objects.all()
    serializer_class = BedroomsBathroomsSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'bedrooms_bathrooms'

# 3. Bedrooms
class BedroomsViewSet(ESModelViewSet):
    queryset = Bedrooms.objects.all()
    serializer_class = BedroomsSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'bedrooms'

# 4. LivingRooms
class LivingRoomsViewSet(ESModelViewSet):
    queryset = LivingRooms.objects.all()
    serializer_class = LivingRoomsSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'living_rooms'

# 5. Bathroom
class BathroomViewSet(ESModelViewSet):
    queryset = Bathroom.objects.all()
    serializer_class = BathroomSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'bathroom'

# 6. Availability
class AvailabilityViewSet(ESModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    ordering_fields = []
    search_fields = []
    index_name = 'availability'

# 7. Pricing
class PricingViewSet(ESModelViewSet):
    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'pricing'

# 8. Deposits
class DepositsViewSet(ESModelViewSet):
    queryset = Deposits.objects.all()
    serializer_class = DepositsSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'deposits'

# 9. FeeAccounts
class FeeAccountsViewSet(ESModelViewSet):
    queryset = FeeAccounts.objects.all()
    serializer_class = FeeAccountsSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'fee_accounts'

# 10. DebitAccount
class DebitAccountViewSet(ESModelViewSet):
    queryset = DebitAccount.objects.all()
    serializer_class = DebitAccountSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'debit_account'

# 11. CreditAccount
class CreditAccountViewSet(ESModelViewSet):
    queryset = CreditAccount.objects.all()
    serializer_class = CreditAccountSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'credit_account'

# 12. RefundPolicies
class RefundPoliciesViewSet(ESModelViewSet):
    queryset = RefundPolicies.objects.all()
    serializer_class = RefundPoliciesSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'refund_policies'

# 13. Units
class UnitsViewSet(ESModelViewSet):
    queryset = Units.objects.all()
    serializer_class = UnitsSerializer
    ordering_fields = []
    search_fields = []
    index_name = 'units'


# 1. Property
class PropertyViewSet(ESModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    ordering_fields = ['name', 'created_at']
    search_fields = ['name', 'summary_headline', 'summary_description']
    index_name = 'property'

# 2. ImagesProperty
class ImagesPropertyViewSet(ESModelViewSet):
    queryset = ImagesProperty.objects.all()
    serializer_class = ImagesPropertySerializer
    ordering_fields = ['order', 'created_at']
    search_fields = ['label']
    index_name = 'images_property'

# 3. PropertyLocation
class PropertyLocationViewSet(ESModelViewSet):
    queryset = PropertyLocation.objects.all()
    serializer_class = PropertyLocationSerializer
    # ordering_fields = ['adr_city', 'created_at']
    # search_fields = ['adr_city', 'adr_state', 'adr_country']
    index_name = 'property_location'


# 4. GuestControls
class GuestControlsViewSet(ESModelViewSet):
    queryset = GuestControls.objects.all()
    serializer_class = GuestControlsSerializer
    ordering_fields = ['created_at']
    search_fields = []  # no full-text fields
    index_name = 'guest_controls'


class TaxAccountsViewSet(ESModelViewSet):
    queryset = TaxAccounts.objects.all()
    serializer_class = TaxAccountsSerializer
    index_name = 'tax_accounts'

    def get_queryset(self):
        """
        Optionally restricts the returned tax accounts to a given organization,
        by filtering against an `organization_id` query parameter in the URL.
        """
        queryset = TaxAccounts.objects.all()
        organization_id = self.request.query_params.get('organization_id', None)
        if organization_id is not None:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

class DeductionAccountsViewSet(ESModelViewSet):
    queryset = DeductionAccounts.objects.all()
    serializer_class = DeductionAccountsSerializer
    index_name = 'deduction_accounts'

    def get_queryset(self):
        """
        Optionally restricts the returned deduction accounts to a given organization,
        by filtering against an `organization_id` query parameter in the URL.
        """
        queryset = DeductionAccounts.objects.all()
        organization_id = self.request.query_params.get('organization_id', None)
        if organization_id is not None:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

class InventoryItemViewSet(ESModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    index_name = 'inventory_items'

    def get_queryset(self):
        """
        Optionally filter by organization_id
        """
        queryset = InventoryItem.objects.all()
        organization_id = self.request.query_params.get("organization_id")
        if organization_id is not None:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

class UsageAccountViewSet(ESModelViewSet):
    queryset = UsageAccount.objects.all()
    serializer_class = UsageAccountSerializer
    index_name = 'usage_accounts'   

    def get_queryset(self):
        """
        Optionally filter by organization_id
        """
        queryset = InventoryItem.objects.all()
        organization_id = self.request.query_params.get("organization_id")
        if organization_id is not None:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

class LynnbrookAccountViewSet(ESModelViewSet):
    queryset = LynnbrookAccount.objects.all()
    serializer_class = LynnbrookAccountSerializer
    index_name = 'lynnbrook_accounts'

    def get_queryset(self):
        queryset = super().get_queryset()
        org_id = self.request.query_params.get('organization_id')
        if org_id:
            queryset = queryset.filter(organization_id=org_id)
        return queryset