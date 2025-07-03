from django.contrib import admin
from .models import OrganizationType, Organization ,Brand

from core.mixin_es import ElasticSearchMixin  # Make sure this is the correct path to your mixin

# ✅ Proper mixin for ES indexing from Admin
class ElasticsearchAdminMixin(ElasticSearchMixin):
    index_name = None  # must be defined in subclass

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if self.index_name:
            print(f"📦 Indexing {obj} into {self.index_name}")
            self.index_instance(obj, self.index_name)

    def delete_model(self, request, obj):
        if self.index_name:
            print(f"❌ Removing {obj} from {self.index_name}")
            self.clear_index(obj, self.index_name)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if self.index_name:
                self.clear_index(obj, self.index_name)
        super().delete_queryset(request, queryset)

# class GenericModelAdmin:
#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#         self.index_instance(obj, self.index_name)  # Sync cache and Elasticsearch

#     def delete_model(self, request, obj):
#         self.clear_index(obj, self.index_name)  # Remove from cache and index
#         super().delete_model(request, obj)
        
#     def delete_queryset(self, request, queryset):
#         for obj in queryset:
#             self.clear_index(obj, self.index_name)  # Clear from ES
#         super().delete_queryset(request, queryset)
  
class OrganizationAdmin(ElasticSearchMixin,admin.ModelAdmin):
    index_name = "organization"  # Same as defined in your viewset
    list_filter = ('user',)  # 👈 Add filters here

class BrandAdmin(ElasticsearchAdminMixin,admin.ModelAdmin,):
    index_name = "brand"  # Same as defined in your viewset
    list_filter = ('organization',)  # 👈 Add filters here



admin.site.register(Brand,BrandAdmin)
admin.site.register(Organization, OrganizationAdmin)

