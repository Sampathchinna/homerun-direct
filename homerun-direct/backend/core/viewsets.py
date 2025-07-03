from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

class GenericResponseMixin:
    """
    A Mixin that standardizes API responses for all ViewSets.
    """

    def format_success_response(self, data, message="Success", status_code=status.HTTP_200_OK):
        """
        Standardized success response format.
        """
        return Response(
            {
                "status": "success",
                "message": message,
                "data": data,
                "errors": None,
                "statusCode": status_code,
            },
            status=status_code,
        )

    def format_error_response(self, errors, message="Validation error", status_code=status.HTTP_400_BAD_REQUEST):
        """
        Standardized error response format.
        """
        return Response(
            errors,
            status=status_code,
        )


class GenericModelViewSet(ModelViewSet, GenericResponseMixin):
    def list(self, request, *args, **kwargs):
        """Cache GET response"""
        cache_key = f"{self.__class__.__name__}_list"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)  # 5 minutes
        return response

    def retrieve(self, request, *args, **kwargs):
        """Cache individual object retrieval"""
        cache_key = f"{self.__class__.__name__}_detail_{kwargs['pk']}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response

    def create(self, request, *args, **kwargs):
        """Clear cache on create"""
        response = super().create(request, *args, **kwargs)
        cache.delete_pattern(f"{self.__class__.__name__}_*")
        return response

    def update(self, request, *args, **kwargs):
        """Clear cache on update"""
        response = super().update(request, *args, **kwargs)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",response)
        cache.delete_pattern(f"{self.__class__.__name__}_*")
        return response

    def destroy(self, request, *args, **kwargs):
        """Clear cache on delete"""
        response = super().destroy(request, *args, **kwargs)
        cache.delete_pattern(f"{self.__class__.__name__}_*")
        return response
