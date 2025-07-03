# organization/tests/test_organization_pagination.py

import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator

from organization.pagination import CustomPagination


@pytest.mark.django_db
def test_custom_pagination_response_structure():
    factory = APIRequestFactory()
    drf_request = Request(factory.get('/fake-url/?page=1'))
    
    data = [{'id': i} for i in range(1, 21)]  # 20 items
    paginator = Paginator(data, 5)  # 5 per page
    page = paginator.page(1)

    pagination = CustomPagination()
    pagination.request = drf_request
    pagination.page = page

    response = pagination.get_paginated_response(page.object_list)

    assert isinstance(response, Response)
    assert "pagination" in response.data  # Corrected this line
    assert response.data["pagination"]["count"] == 20
    assert response.data["pagination"]["per_page"] == 5
    assert response.data["pagination"]["previous"] is None
    assert response.data["pagination"]["next"] is not None



@pytest.mark.django_db
def test_custom_pagination_with_query_param():
    factory = APIRequestFactory()
    drf_request = Request(factory.get('/fake-url/?page=2&per_page=3'))
    
    data = [{'id': i} for i in range(1, 10)]  # 9 items
    paginator = Paginator(data, 3)
    page = paginator.page(2)

    pagination = CustomPagination()
    pagination.request = drf_request
    pagination.page = page

    response = pagination.get_paginated_response(page.object_list)

    assert response.data["pagination"]["count"] == 9
    assert response.data["pagination"]["per_page"] == 3
    assert response.data["pagination"]["previous"] is not None
    assert response.data["pagination"]["next"] is not None


@pytest.mark.django_db
def test_custom_pagination_no_results():
    factory = APIRequestFactory()
    drf_request = Request(factory.get('/fake-url/?page=1'))

    data = []
    paginator = Paginator(data, 5)
    page = paginator.page(1)

    pagination = CustomPagination()
    pagination.request = drf_request
    pagination.page = page

    response = pagination.get_paginated_response(page.object_list)

    assert response.data["pagination"]["count"] == 0
    assert response.data["pagination"]["per_page"] == 5
    assert response.data["pagination"]["previous"] is None
    assert response.data["pagination"]["next"] is None
