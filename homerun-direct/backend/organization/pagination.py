from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 5  # Default items per page
    page_size_query_param = 'per_page'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "response": data,
                "pagination": OrderedDict(
                    [
                        ("count", self.page.paginator.count),
                        ("per_page", self.get_page_size(self.request)),
                        ("previous", self.get_previous_link()),
                        ("next", self.get_next_link()),
                    ]
                ),
            }
        )
