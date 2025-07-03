import json
from redis import Redis
from elasticsearch import Elasticsearch
from django.core.serializers.json import DjangoJSONEncoder
from elasticsearch import Elasticsearch

es_client = Elasticsearch(
    [{"host": "localhost", "port": 9200, "scheme": "http"}]  # Add "scheme": "http"
)

# Initialize Redis & Elasticsearch clients
redis_client = Redis(host="localhost", port=6379, db=0)

def update_cache(organization):
    from organization.models import Organization
    """
    Updates the given organization in Redis and Elasticsearch.

    :param organization: Organization object
    """
    if not organization:
        return

    # ✅ Convert Organization instance to dictionary
    organization_data = {
        "id": organization.id,
        "organization_name": organization.organization_name,
        "user_email": organization.user.email if organization.user else None,
        "subscription_plan": organization.subscription_plan.name if organization.subscription_plan else None,
        "stripe_subscription_id": organization.stripe_subscription_id,
        "is_organization_created": organization.is_organization_created,
        "is_payment_done": organization.is_payment_done,
        "location": {
            "street_address": organization.location.street_address if organization.location else None,
            "city": organization.location.city if organization.location else None,
            "state_province": organization.location.state_province if organization.location else None,
            "postal_code": organization.location.postal_code if organization.location else None,
            "country": organization.location.country if organization.location else None,
            "latitude": float(organization.location.latitude) if organization.location and organization.location.latitude else None,
            "longitude": float(organization.location.longitude) if organization.location and organization.location.longitude else None,
        },
        "created_at": organization.created_at.isoformat(),
    }

    # ✅ Store in Redis
    redis_key = f"organization:{organization.id}"
    redis_client.set(redis_key, json.dumps(organization_data, cls=DjangoJSONEncoder))

    # ✅ Store in Elasticsearch
    es_index = "organizations"
    es_client.index(index=es_index, id=organization.id, body=organization_data)

    print(f"✅ Cache updated for Organization ID {organization.id}")
