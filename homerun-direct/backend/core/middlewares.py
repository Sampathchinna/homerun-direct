import uuid
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from elasticsearch import Elasticsearch
from django.conf import settings

logger = logging.getLogger(__name__)


class APILoggingMiddleware(MiddlewareMixin):
    async_mode = False  # ✅ Required for Django 5.1+

    def __init__(self, get_response):
        self.get_response = get_response
        self.es = Elasticsearch(settings.ELASTICSEARCH_DSL["default"]["hosts"])

    def process_request(self, request):
        request.request_id = str(uuid.uuid4())

    def process_response(self, request, response):
        if request.path.startswith("/auth"):
            return response

        def sanitize_body(data, max_keys=10):
            if isinstance(data, dict):
                return {k: str(data[k])[:100] for k in list(data)[:max_keys]}
            return str(data)[:300]

        try:
            raw_body = json.loads(response.content.decode("utf-8")) if response.get("Content-Type", "").startswith("application/json") else None
            body = sanitize_body(raw_body)
        except Exception as e:
            logger.warning(f"Could not decode response body: {e}")

        log_data = {
            "request_id": getattr(request, "request_id", str(uuid.uuid4())),
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "user": request.user.id if hasattr(request, "user") and request.user.is_authenticated else None,
            "body": body
        }

        try:
            self.es.index(index="api_logs", body=log_data)
        except Exception as e:
            logger.error(f"Failed to index log to Elasticsearch: {e}")

        return response
