from core.mixin_es import es

from django.conf import settings
from django.shortcuts import get_object_or_404
from core.viewsets import GenericModelViewSet
from rest_framework import  status ,filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import (
    Organization,Brand, BrandFooters, BrandHeaders, BrandInfos, BrandHomePages,BrandPages,
    BrandPageSliceHeadline, BrandPageSliceAmenities, BrandPageSliceFeaturedListings,
    BrandPageSliceGridContentBlocks, BrandPageSliceHeadline, BrandPageSliceHomepageHeros,
    BrandPageSliceLocalActivities, BrandPageSliceMediaContentBlocks, BrandPageSlicePhotoGalleries,
    BrandPageSlicePullQuotes, BrandPageSliceReviews, BrandPageSliceSingleImages, BrandPageSliceVideoEmbeds,
    BrandPageSlices, BrandsEmployees
)
from .serializers import (
    OrganizationSerializer,BrandSerializer, BrandFootersSerializer, BrandHomePagesSerializer,BrandHeadersSerializer,
    BrandInfosSerializer, BrandPagesSerializer, BrandPageSliceHeadlineSerializer,
    BrandPageSliceAmenitiesSerializer, BrandPageSliceFeaturedListingsSerializer,
    BrandPageSliceGridContentBlocksSerializer,
    BrandPageSliceHomepageHerosSerializer, BrandPageSliceLocalActivitiesSerializer,
    BrandPageSliceMediaContentBlocksSerializer, BrandPageSlicePhotoGalleriesSerializer,
    BrandPageSlicePullQuotesSerializer, BrandPageSliceReviewsSerializer,
    BrandPageSliceSingleImagesSerializer, BrandPageSliceVideoEmbedsSerializer,
    BrandPageSlicesSerializer, BrandsEmployeesSerializer
)
from django.contrib.auth import get_user_model
from payment.services.stripe_service import create_checkout_session
from core.pagination import CustomPagination
from rest_framework_simplejwt.tokens import RefreshToken
from core.mixin_es import ElasticSearchMixin
import stripe
from core.mixin_redis import RedisCacheMixin
from urllib.parse import urlencode


from rbac.org_level_permission import apply_organization_level_filter,apply_brand_level_filter
User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

class ESModelViewSet(ElasticSearchMixin, GenericModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    pagination_class = CustomPagination
    redis_cache = RedisCacheMixin()

    def get_searchable_fields(self):
        # Get all field names dynamically from the model
        model_fields = self.queryset.model._meta.get_fields()

        # Dynamically filter out fields that we can search (e.g., CharFields, TextFields)
        searchable_fields = [
            field.name
            for field in model_fields
            if isinstance(field, (models.CharField, models.TextField))
        ]
        
        # You can also manually add or exclude specific fields if needed
        searchable_fields = [field for field in searchable_fields if field != 'id']  # exclude 'id' if you don't want it

        return searchable_fields

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
                    'fields': searchable_fields,
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


class BrandViewSet(ElasticSearchMixin, GenericModelViewSet):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()
    filter_backends = [filters.OrderingFilter]
    pagination_class = CustomPagination
    search_fields = ['name', 'description', 'currency', 'language']
    ordering_fields = ['name', 'created_at']
    index_name = "brand"
    redis_cache = RedisCacheMixin()

    def get_queryset(self):
        qs = Brand.objects.all()
        if self.action in ['update', 'partial_update', 'retrieve']:  # <-- skip permission filter
            return qs
        if not self.redis_cache.has_all_org_access(self.request.user):
            org_ids = self.redis_cache.get_user_org_ids(self.request.user)
            qs = qs.filter(id__in=org_ids)
        return qs
    
    

    def list(self, request, *args, **kwargs):
        page = int(request.query_params.get("page", 1))
        per_page = int(request.query_params.get("per_page", 50))

        filters = request.query_params
        must_clauses = self.build_elasticsearch_filters(filters)

        # 🔐 Apply session-based brand permission filtering
        apply_brand_level_filter(request, must_clauses)

        search_query = request.query_params.get("search")
        if search_query:
            must_clauses.append({
                "multi_match": {
                    "query": search_query,
                    "fields": [
                        "organization"
                        "name",
                        "description",
                        "currency",
                        "language",
                        "date_format",
                        "verify_image",
                        "verify_image_description",
                        "verify_signature",
                        "cms_version"
                    ]
                }
            })
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",must_clauses)
        query = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            }
        }

        try:
            results = self.search_elasticsearch(
                index_name=self.index_name,
                query=query,
                page=page,
                per_page=per_page
            )
            return Response({
                "response": results,
                "pagination": {
                    "count": len(results),
                    "per_page": per_page,
                    "previous": None if page == 1 else page - 1,
                    "next": None if len(results) < per_page else page + 1
                }
            }, status=200)
        except Exception as e:
            print("🔥 Elasticsearch failed:", e)
            return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        self.index_instance(instance, self.index_name)
        self.redis_cache.set_user_org_session(self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
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
            print("🔥 ES retrieve failed:Falling back to DB", e)
            return super().retrieve(request, *args, **kwargs)



class OrganizationViewSet(ElasticSearchMixin,GenericModelViewSet):
    
    serializer_class = OrganizationSerializer
    
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['organization_name', 'created_at', 'user__email']
    pagination_class = CustomPagination #StandardResultsSetPagination
    search_fields = [
        'organization_name',
        'organization_type__value',
        'language__name',
        'currency__code',
        'company_type__name',
        'payment_processor__name',
        'location__city',
        'location__country',
        'subscription_plan__name',
        'user__email',
        'user__first_name',
        'user__last_name',
        'stripe_subscription_id'
    ]
    ordering_fields = [
        'organization_name', 'created_at', 'subscription_plan__name', 'user__email'
    ]
    index_name = "organization"  # Define your Elasticsearch index name
    redis_cache = RedisCacheMixin()
    # ✅ ADD this queryset as a fallback
    queryset = Organization.objects.all()

    def get_queryset(self):
        qs = Organization.objects.all()
        if self.action in ['update', 'partial_update', 'retrieve']:  # <-- skip permission filter
            return qs
        if not self.redis_cache.has_all_org_access(self.request.user):
            org_ids = self.redis_cache.get_user_org_ids(self.request.user)
            qs = qs.filter(id__in=org_ids)
        return qs   
    def list(self, request, *args, **kwargs):
        page = int(request.query_params.get("page", 1))
        per_page = int(request.query_params.get("per_page", 50))

        excluded_keys = {"page", "per_page", "search", "ordering"}
        filters = request.query_params
        must_clauses = self.build_elasticsearch_filters(filters)
        # 🔐 Apply org access filtering if not super admin
        apply_organization_level_filter(request, must_clauses)


        # Optional: Add full-text search
        search_query = request.query_params.get("search")
        if search_query:
            must_clauses.append({
                "multi_match": {
                    "query": search_query,
                    "fields": [
                        "organization_name",
                        "organization_type",
                        "language",
                        "currency",
                        "company_type",
                        "payment_processor",
                        "location.city",
                        "location.country",
                        "location.street_address",
                        "location.apt_suite",
                        "location.state_province",
                        "location.postal_code",
                        "subscription_plan",
                        "user.email",
                        "user.first_name",
                        "user.last_name",
                        "stripe_subscription_id"
                    ],
                    "type": "best_fields"
                }
            })

        query = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            }
        }

        try:
            results = self.search_elasticsearch(
                index_name=self.index_name,
                query=query,
                page=page,
                per_page=per_page
            )
            base_url = request.build_absolute_uri(request.path)
            query_dict = request.query_params.copy()

            def build_url(target_page):
                query_dict["page"] = target_page
                query_dict["per_page"] = per_page
                return f"{base_url}?{urlencode(query_dict)}"

            previous_url = build_url(page - 1) if page > 1 else None
            next_url = build_url(page + 1) if len(results) == per_page else None

            return Response({
                "response": results,
                "pagination": {
                    "count": len(results),
                    "per_page": per_page,
                    "previous": None if page == 1 else page - 1,
                    "next": None if len(results) < per_page else page + 1
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print("⚠️ Elasticsearch fallback due to error:", e)
            return None #self.get_queryset()


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

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            print("***********************************************************")
            es_doc = es.get(index=self.index_name, id=pk)["_source"]
        except Exception:
            return Response({"detail": "Not found."}, status=404)

        return Response(es_doc)


    @action(detail=False, methods=['post'],url_path="create-checkout-session")
    def create_checkout_session(self, request):
        user = request.user
        subscription_plan_id = request.data.get("subscription_plan_id")
        organization_id = request.data.get("organization_id")

        if not subscription_plan_id or not organization_id:
            return Response({"error": "Required fields missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = create_checkout_session(user, subscription_plan_id, organization_id)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({"session_url": session.url, "session_id": session.id,"access_token": access_token,"refresh_token": str(refresh)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'], url_path="verify-payment")
    def verify_payment(self, request):
        """API to verify Stripe checkout session after redirection."""
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response({"error": "Session ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                organization = get_object_or_404(Organization, user=request.user)
                organization.is_payment_done = True
                organization.save()
                
                return Response({
                    "success": True,
                    "message": "Payment verified successfully!",
                    "organization_id": organization.id
                }, status=status.HTTP_200_OK)

            return Response({"success": False, "message": "Payment not completed."}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Define the other Brand-related ViewSets using the same pattern
class BrandFootersViewSet(ESModelViewSet):
    serializer_class = BrandFootersSerializer
    index_name = "brandfooters"
    queryset = BrandFooters.objects.all()
    redis_cache = RedisCacheMixin()


class BrandHeadersViewSet(ESModelViewSet):
    serializer_class = BrandHeadersSerializer
    index_name = "brandheaders"
    queryset = BrandHeaders.objects.all()
    redis_cache = RedisCacheMixin()



class BrandHomePagesViewSet(ESModelViewSet):
    serializer_class = BrandHomePagesSerializer
    index_name = "brandhomepages"
    queryset = BrandHomePages.objects.all()
    redis_cache = RedisCacheMixin()



class BrandInfosViewSet(ESModelViewSet):
    serializer_class = BrandInfosSerializer
    index_name = "brandinfos"
    queryset = BrandInfos.objects.all()
    redis_cache = RedisCacheMixin()


class BrandPagesViewSet(ESModelViewSet):
    serializer_class = BrandPagesSerializer
    index_name = "brandpages"
    queryset = BrandPages.objects.all()
    redis_cache = RedisCacheMixin()


class BrandPageSliceHeadlineViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceHeadlineSerializer
    index_name = "brandpagesliceheadline"
    queryset = BrandPageSliceHeadline.objects.all()
    redis_cache = RedisCacheMixin()

class BrandPageSliceAmenitiesViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceAmenitiesSerializer
    index_name = "brandpagesliceamenities"
    queryset = BrandPageSliceAmenities.objects.all()
    redis_cache = RedisCacheMixin()

class BrandPageSliceFeaturedListingsViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceFeaturedListingsSerializer
    index_name = "brandpageslicefeaturedlistings"
    queryset = BrandPageSliceFeaturedListings.objects.all()
    redis_cache = RedisCacheMixin()

class BrandPageSliceGridContentBlocksViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceGridContentBlocksSerializer
    index_name = "brandpageslicegridcontentblocks"
    queryset = BrandPageSliceGridContentBlocks.objects.all()
    redis_cache = RedisCacheMixin()


class BrandPageSliceHeadlinesViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceHeadlineSerializer
    index_name = "brandpagesliceheadlines"
    queryset = BrandPageSliceHeadline.objects.all()
    redis_cache = RedisCacheMixin()



class BrandPageSliceHomepageHerosViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceHomepageHerosSerializer
    index_name = "brandpageslicehomepageheros"
    queryset = BrandPageSliceHomepageHeros.objects.all()
    redis_cache = RedisCacheMixin()


class BrandPageSliceLocalActivitiesViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceLocalActivitiesSerializer
    index_name = "brandpageslicelocalactivities"
    queryset = BrandPageSliceLocalActivities.objects.all()
    redis_cache = RedisCacheMixin()


class BrandPageSliceMediaContentBlocksViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceMediaContentBlocksSerializer
    index_name = "brandpageslicemediacontentblocks"
    queryset = BrandPageSliceMediaContentBlocks.objects.all()
    redis_cache = RedisCacheMixin()



class BrandPageSlicePhotoGalleriesViewSet(ESModelViewSet):
    serializer_class = BrandPageSlicePhotoGalleriesSerializer
    index_name = "brandpageslicephotogalleries"
    queryset = BrandPageSlicePhotoGalleries.objects.all()
    redis_cache = RedisCacheMixin()


class BrandPageSlicePullQuotesViewSet(ESModelViewSet):
    serializer_class = BrandPageSlicePullQuotesSerializer
    index_name = "brandpageslicepullquotes"
    queryset = BrandPageSlicePullQuotes.objects.all()
    redis_cache = RedisCacheMixin()


class BrandPageSliceReviewsViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceReviewsSerializer
    index_name = "brandpageslicereviews"
    queryset = BrandPageSliceReviews.objects.all()
    redis_cache = RedisCacheMixin()


class BrandPageSliceSingleImagesViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceSingleImagesSerializer
    index_name = "brandpageslicesingleimages"
    queryset = BrandPageSliceSingleImages.objects.all()
    redis_cache = RedisCacheMixin()

class BrandPageSliceVideoEmbedsViewSet(ESModelViewSet):
    serializer_class = BrandPageSliceVideoEmbedsSerializer
    index_name = "brandpageslicevideoembeds"
    queryset = BrandPageSliceVideoEmbeds.objects.all()
    redis_cache = RedisCacheMixin()


class BrandPageSlicesViewSet(ESModelViewSet):
    serializer_class = BrandPageSlicesSerializer
    index_name = "brandpageslices"
    queryset = BrandPageSlices.objects.all()
    redis_cache = RedisCacheMixin()

class BrandsEmployeesViewSet(ESModelViewSet):
    serializer_class = BrandsEmployeesSerializer
    index_name = "brandsemployees"
    queryset = BrandsEmployees.objects.all()

    redis_cache = RedisCacheMixin()


  