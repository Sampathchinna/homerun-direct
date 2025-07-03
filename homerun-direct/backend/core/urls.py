from django.urls import path
from core.viewsets import GenericModelViewSet

entity_list = GenericModelViewSet.as_view({"get": "list", "post": "create"})
entity_detail = GenericModelViewSet.as_view(
    {"get": "retrieve", "put": "update", "delete": "destroy"}
)
urlpatterns = [
    path(
        "api/entities/", entity_list, name="entity-list"
    ),  # ✅ Fix for test_create_entity_success
    path(
        "api/entities/<int:pk>/", entity_detail, name="entity-detail"
    ),  # ✅ Fix for test_update_entity_success
    path(
        "api/entities/metadata/",
        GenericModelViewSet.as_view({"get": "metadata"}),
        name="entity-metadata",
    )
]
