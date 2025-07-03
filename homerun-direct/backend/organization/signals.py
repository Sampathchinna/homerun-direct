from django.db.models.signals import post_save
from django.dispatch import receiver
from master.models import (
    Language, Currency,
    CompanyType, PaymentProcessor, Location, SubscriptionPlan
)
from .models import Organization
from core.mixin_es import ElasticSearchMixin

cache_search = ElasticSearchMixin()

def reindex_related_entity_by_fk(model, fk_field: str):
    @receiver(post_save, sender=model)
    def _reindex(sender, instance, **kwargs):
        filter_kwargs = {fk_field: instance}
        orgs = Organization.objects.filter(**filter_kwargs)
        for org in orgs:
            cache_search.index_instance(org, "organization")
    return _reindex

# Connect signals here:
#reindex_related_entity_by_fk(OrganizationType, "organization_type")
reindex_related_entity_by_fk(Language, "language")
reindex_related_entity_by_fk(Currency, "currency")
reindex_related_entity_by_fk(CompanyType, "company_type")
reindex_related_entity_by_fk(PaymentProcessor, "payment_processor")
reindex_related_entity_by_fk(Location, "location")
reindex_related_entity_by_fk(SubscriptionPlan, "subscription_plan")
