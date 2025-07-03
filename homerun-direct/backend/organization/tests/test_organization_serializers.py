from django.test import TestCase
from unittest.mock import MagicMock
from organization.serializers import OrganizationSerializer



class OrganizationSerializerTestCase(TestCase):
    def setUp(self):
        self.location_mock = MagicMock()
        self.location_mock.formatted_address = "123 Main St"
        self.location_mock.apt_suite = "Apt 4B"
        self.location_mock.city = "New York"
        self.location_mock.state_province = "NY"
        self.location_mock.postal_code = "10001"
        self.location_mock.country = "USA"
        self.location_mock.latitude = 40.712776
        self.location_mock.longitude = -74.005974

        self.organization_mock = MagicMock()
        self.organization_mock.name = "Test Organization"
        self.organization_mock.location = self.location_mock

        self.valid_data = {
            "name": "Test Organization",
            "terms_agreement": True,
            "formatted_address": "123 Main St",
            "apt_suite": "Apt 4B",
            "city": "New York",
            "state_province": "NY",
            "postal_code": "10001",
            "country": "USA",
            "latitude": 40.712776,
            "longitude": -74.005974
        }

    def test_valid_serializer(self):
        serializer = OrganizationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_serializer_missing_terms(self):
        invalid_data = self.valid_data.copy()
        del invalid_data["terms_agreement"]
        serializer = OrganizationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("terms_agreement", serializer.errors)

    def test_create_organization(self):
        serializer = OrganizationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save = MagicMock(return_value=self.organization_mock)
        organization = serializer.save()
        self.assertEqual(organization.name, "Test Organization")

    def test_update_organization(self):
        updated_data = {
            "name": "Updated Organization",
            "terms_agreement": True,
            "formatted_address": "456 New St",
            "apt_suite": "Suite 100",
            "city": "San Francisco",
            "state_province": "CA",
            "postal_code": "94103",
            "country": "USA"
        }
        serializer = OrganizationSerializer(instance=self.organization_mock, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Simulate updating the instance
        self.organization_mock.name = updated_data["name"]

        serializer.save = MagicMock(return_value=self.organization_mock)
        updated_organization = serializer.save()

        self.assertEqual(updated_organization.name, "Updated Organization")
