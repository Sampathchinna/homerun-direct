import json
from elasticsearch import Elasticsearch
from django.conf import settings
from django.db.models.query import QuerySet
from elasticsearch.helpers import bulk
from core.models import *
from organization.models import *
from property.models import *
from rbac.models import *
import re
from rest_framework.exceptions import ValidationError
from datetime import date, datetime, time
from decimal import Decimal

es = Elasticsearch(settings.ELASTICSEARCH_DSL["default"]["hosts"])

# Generic Elasticsearch utility
class ElasticsearchIndexMixin:
    def serialize_for_elasticsearch(self,data):
        def convert(value):
            if isinstance(value, (datetime, date, time)):
                return value.isoformat()
            elif isinstance(value, Decimal):
                return float(value)
            elif isinstance(value, list):
                return [convert(item) for item in value]
            elif isinstance(value, dict):
                if "meta_tags" in value and isinstance(value["meta_tags"], dict):
                    value["meta_tags"] = json.dumps(value["meta_tags"])
                return {k: convert(v) for k, v in value.items()}
            return value
        if "meta_tags" in data and isinstance(data["meta_tags"], dict):
            data["meta_tags"] = json.dumps(data["meta_tags"])
        return {k: convert(v) for k, v in data.items()}

    def index_to_elasticsearch(self, instance, index_name):
        data = self.serialize_instance(instance)
        serialized_doc = self.serialize_for_elasticsearch(data)
        es.index(index=index_name, id=instance.pk, body=serialized_doc)

    def delete_from_elasticsearch(self, pk, index_name):
        es.delete(index=index_name, id=pk, ignore=[404])

    def serialize_instance(self, instance):
        # Default to model's to_dict() or full model data
        from django.db.models import Model
        data = {}

        # Get flat model fields first
        for field in instance._meta.fields:
            field_name = field.name
            value = getattr(instance, field_name)
            if isinstance(value, Model):
                data[field_name] = value.pk  # Store FK as ID
            else:
                data[field_name] = value

        # Flatten Location extra fields
        location = getattr(instance, "location", None)
        if isinstance(location, Location):
            data["street_address"] = location.street_address
            data["apt_suite"] = location.apt_suite
            data["city"] = location.city
            data["state_province"] = location.state_province
            data["postal_code"] = location.postal_code
            data["country"] = location.country
            data["latitude"] = location.latitude
            data["longitude"] = location.longitude

        if isinstance(instance, Property):
            org_prop = OrganizationProperty.objects.filter(property=instance).first()
            data["organization_id"] = org_prop.organization.id if org_prop and org_prop.organization else None

        return data

    def search_elasticsearch(self, index_name, query, page=1, per_page=20):
        print(index_name)
        print(query)
        from math import ceil
        start = (page - 1) * per_page
        print("⚙️ Querying Elasticsearch:", json.dumps(query, indent=2))  # Debug line
        response = es.search(
            index=index_name,
            body=query,
            from_=start,
            size=per_page
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def build_elasticsearch_filters(self, query_params):
        """
        Build a list of ES 'must' clauses from DRF request.query_params, supporting:
        - __in, __gte, __lte, __gt, __lt
        - __icontains, __istartswith
        - boolean true/false
        - comma-separated multi-value
        - nested fields (dot notation) wrapped in 'nested' query
        """
        must_clauses = []
        # regex to split a key into field path and optional op suffix
        pattern = re.compile(r'^(?P<field>[\w\.]+?)(?:__(?P<op>in|gte|lte|gt|lt|icontains|istartswith))?$')

        for raw_key, raw_val in query_params.items():
            # control params
            if raw_key in {"page", "per_page", "search", "ordering"}:
                continue

            m = pattern.match(raw_key)
            if not m:
                # fallback: treat as a simple match
                must_clauses.append({"match": {raw_key: raw_val}})
                continue

            field, op = m.group("field"), m.group("op")
            val = raw_val

            # build the inner clause dict
            if op == "in":
                clause = {"terms": {field: val.split(",")}}
            elif op in {"gte", "lte", "gt", "lt"}:
                range_key = op
                clause = {"range": {field: {range_key: val}}}
            elif op == "icontains":
                clause = {"wildcard": {field: f"*{val.lower()}*"}}
            elif op == "istartswith":
                clause = {"prefix": {field: val.lower()}}
            else:
                # no suffix: detect boolean / multi / match
                low = isinstance(val, str) and val.lower()
                if low in {"true", "false"}:
                    clause = {"term": {field: low == "true"}}
                elif isinstance(val, str) and "," in val:
                    clause = {"terms": {field: val.split(",")}}
                else:
                    clause = {"match": {field: val}}

            # if this is a nested path, wrap it
            if "." in field:
                path = field.split(".")[0]
                must_clauses.append({
                    "nested": {
                        "path": path,
                        "query": clause
                    }
                })
            else:
                must_clauses.append(clause)

        return must_clauses


class ElasticSearchMixin(ElasticsearchIndexMixin):
    def index_instance(self, instance, index_name):
        self.index_to_elasticsearch(instance, index_name)

    def clear_index(self, instance, index_name):
        self.delete_from_elasticsearch(instance.pk, index_name)

    def bulk_index_queryset(self, queryset: QuerySet, index_name):
        actions = [
            {
                "_index": index_name,
                "_id": obj.pk,
                "_source": self.serialize_instance(obj)
            }
            for obj in queryset
        ]
        bulk(es, actions)