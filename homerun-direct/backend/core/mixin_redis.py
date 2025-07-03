from django.core.cache import cache

class RedisCacheMixin:
    cache_timeout = 60 * 60  # 1 hour

    def get_cache_key(self, model_name, pk=None):
        key = f"{model_name.lower()}"
        if pk:
            key += f":{pk}"
        return key

    def get_from_cache(self, model_name, pk):
        key = self.get_cache_key(model_name, pk)
        return cache.get(key)

    def set_to_cache(self, model_name, pk, data):
        key = self.get_cache_key(model_name, pk)
        cache.set(key, data, timeout=self.cache_timeout)

    def delete_cache(self, model_name, pk=None):
        key = self.get_cache_key(model_name, pk)
        cache.delete(key)

    def set_user_org_session(self, user):
        """
        Stores all organization data related to the user in Redis.
        """
        from organization.models import Organization  # Avoid circular import
        from organization.serializers import OrganizationSerializer  # Ensure serializer exists

        if user.is_superuser:
            orgs = Organization.objects.all()
            cache.set(f"user:{user.id}:all_organizations", True, timeout=self.cache_timeout)
        else:
            orgs = Organization.objects.filter(user=user)
            cache.set(f"user:{user.id}:all_organizations", False, timeout=self.cache_timeout)

        org_ids = []
        org_data = []
        for org in orgs:
            org_ids.append(org.id)
            serialized = OrganizationSerializer(org).data
            org_data.append(serialized)

        cache.set(f"user:{user.id}:organization_ids", org_ids, timeout=self.cache_timeout)
        cache.set(f"user:{user.id}:organizations", org_data, timeout=self.cache_timeout)

    def get_user_org_ids(self, user):
        return cache.get(f"user:{user.id}:organization_ids", [])

    def get_user_orgs(self, user):
        return cache.get(f"user:{user.id}:organizations", [])

    def has_all_org_access(self, user):
        return cache.get(f"user:{user.id}:all_organizations", False)