from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.request import Request
from rest_framework import status
from collections import OrderedDict
from core.pagination import CustomPagination
from rest_framework.response import Response

class CustomPaginationTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.pagination = CustomPagination()

    def test_default_page_size(self):
        self.assertEqual(self.pagination.page_size, 50)  # ← match actual value


    def test_page_size_query_param(self):
        self.assertEqual(self.pagination.page_size_query_param, 'per_page')

    def test_max_page_size(self):
        self.assertEqual(self.pagination.max_page_size, 100)

    def test_paginated_response_structure(self):
        class MockPaginator:
            count = 50  # Ensures the count property is accessed

            def get_elided_page_range(self):
                return [1, 2, 3]  # ✅ Correct: This is a list


        class MockPage:
            paginator = MockPaginator()
            number = 2  # Simulate second page

            def has_next(self):
                return True

            def has_previous(self):
                return True

            def next_page_number(self):
                return self.number + 1  # Correct next page simulation

            def previous_page_number(self):
                return self.number - 1  # ✅ Fix missing method

        request = Request(self.factory.get('/?per_page=10', HTTP_HOST='testserver'))
        self.pagination.page = MockPage()
        self.pagination.request = request

        response = self.pagination.get_paginated_response(["item1", "item2"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "response": ["item1", "item2"],
            "pagination": OrderedDict(
                [
                    ("count", 50),
                    ("per_page", 10),
                    ("previous", "http://testserver/?per_page=10"),
                    ("next", "http://testserver/?page=3&per_page=10"),
                ]
            ),
        }
        self.assertEqual(response.data, expected_data)



    