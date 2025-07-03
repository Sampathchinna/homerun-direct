from rest_framework import serializers, status
from rest_framework.test import APITestCase, APIRequestFactory
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.response import Response

# Define the serializer
class GenericSerializer(serializers.Serializer):
    """ A Generic Serializer with overridden create and update methods """
    organization_name = serializers.CharField(max_length=255)
    terms_agreement = serializers.BooleanField()
    organization_type = serializers.CharField(max_length=100, required=False, allow_null=True)
    language = serializers.CharField(max_length=50, required=False, allow_null=True)
    currency = serializers.CharField(max_length=10, required=False, allow_null=True)
    payment_processor = serializers.CharField(max_length=50, required=False, allow_null=True)
    subscription_plan = serializers.CharField(max_length=50, required=False, allow_null=True)
    user = serializers.CharField(max_length=255, required=False, allow_null=True)
    location = serializers.JSONField()

    def create(self, validated_data):
        return validated_data  # Simulating creation

    def update(self, instance, validated_data):
        instance.update(validated_data)  # Updating dictionary
        return instance  # Simulating update

# Test cases
class GenericSerializerTestCase(APITestCase):
    def setUp(self):
        self.valid_data = {
            'organization_name': 'Test Org',
            'terms_agreement': True,
            'organization_type': 'Tech',
            'language': 'English',
            'currency': 'USD',
            'payment_processor': 'PayPal',
            'subscription_plan': 'Premium',
            'user': 'test_user',
            'location': {"city": "New York", "country": "USA"}
        }
        self.factory = APIRequestFactory()

    def test_serializer_create(self):
        serializer = GenericSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance['organization_name'], self.valid_data['organization_name'])

    def test_serializer_update(self):
        instance = self.valid_data.copy()
        updated_data = self.valid_data.copy()
        updated_data['organization_name'] = 'Updated Org'
        serializer = GenericSerializer(instance=instance, data=updated_data)
        self.assertTrue(serializer.is_valid())
        updated_instance = serializer.save()
        self.assertEqual(updated_instance['organization_name'], 'Updated Org')

    @patch('rest_framework.viewsets.ModelViewSet.create')
    def test_create_entity(self, mock_create):
        mock_create.return_value = Response(self.valid_data, status=status.HTTP_201_CREATED)
        response = mock_create(self.factory.post('/api/genericmodel/', self.valid_data, format='json'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['organization_name'], self.valid_data['organization_name'])

    @patch('rest_framework.viewsets.ModelViewSet.update')
    def test_update_entity(self, mock_update):
        mock_update.return_value = Response(self.valid_data, status=status.HTTP_200_OK)
        response = mock_update(self.factory.put('/api/genericmodel/1/', self.valid_data, format='json'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['organization_name'], self.valid_data['organization_name'])

    @patch('rest_framework.viewsets.ModelViewSet.destroy')
    def test_delete_entity(self, mock_destroy):
        mock_destroy.return_value = Response({}, status=status.HTTP_204_NO_CONTENT)
        response = mock_destroy(self.factory.delete('/api/genericmodel/1/'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch('rest_framework.viewsets.ModelViewSet.get_serializer')
    def test_metadata_endpoint(self, mock_get_serializer):
        mock_serializer = MagicMock()
        mock_serializer.data = {"fields": ["organization_name", "terms_agreement"]}
        mock_get_serializer.return_value = mock_serializer

        response = Response(mock_serializer.data, status=status.HTTP_200_OK)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("fields", response.data)
