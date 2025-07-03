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

class BookingViewSet(ESModelViewSet):
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer
    ordering_fields = ['name', 'created_at']
    search_fields = ['name']
    index_name = 'booking'
