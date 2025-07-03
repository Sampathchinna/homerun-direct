from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps
from core.models import Entity
from unittest.mock import patch, MagicMock

from django.db import models

class EntityModelTest(TestCase):
     def setUp(self):
         self.entity = Entity.objects.create(
             name="Test Entity",
             url_path="/api/test-entity",
             model_path="auth.User",
         )

     def test_entity_creation(self):
         """Test if Entity object is created successfully with default values"""
         self.assertEqual(self.entity.name, "Test Entity")
         self.assertEqual(self.entity.url_path, "/api/test-entity")
         self.assertEqual(self.entity.model_path, "auth.User")

         # Ensure default JSON fields are initialized correctly
         self.assertEqual(self.entity.meta, {"title": "Test Entity", "description": ""})
         self.assertEqual(self.entity.form["title"], "Test Entity Form")
         self.assertEqual(self.entity.form["entity"], "/api/test-entity")

         # Ensure POST schema is generated
         self.assertTrue(isinstance(self.entity.POST, dict))  # Ensure it's a dict
         self.assertNotEqual(self.entity.POST, {})  # Ensure it's not empty


     def test_str_representation(self):
         """Test __str__ method"""
         self.assertEqual(str(self.entity), "Test Entity - /api/test-entity")

     def test_get_model_class_valid(self):
         """Test get_model_class returns the correct model class"""
         model_class = self.entity.get_model_class()
         self.assertEqual(model_class, apps.get_model("auth", "User"))

     def test_get_model_class_invalid(self):
         """Test get_model_class raises an error for an invalid model_path"""
         self.entity.model_path = "invalid.Model"
         with self.assertRaises(ImproperlyConfigured):
             self.entity.get_model_class()

     @patch("core.models.Entity.get_model_class")
     def test_build_post_schema(self, mock_get_model_class):
         """Test build_post_schema generates the correct schema"""

         # Mock a Django model
         mock_model = MagicMock()

         # Mock a CharField with required attributes
         mock_field = MagicMock(spec=models.CharField)  # Ensure it behaves like a Django CharField
         mock_field.auto_created = False  # Ensure it's not ignored
         mock_field.verbose_name = "Test Field"
         mock_field.name = "test_field"
         mock_field.max_length = 255
         mock_field.blank = False

         # Ensure it returns 'CharField' as its type
         mock_field.get_internal_type.return_value = "CharField"

         # Set the mocked model's fields
         mock_model._meta.get_fields.return_value = [mock_field]

         # Mock get_model_class() to return our fake model
         mock_get_model_class.return_value = mock_model

         # Call the method under test
         schema = self.entity.build_post_schema()

         # Print debug info
         print("Generated POST schema:", schema)  # Debugging output

         # Assertions
         self.assertIn("test_field", schema, f"Expected 'test_field' in schema, but got: {schema}")
         self.assertEqual(schema["test_field"]["type"], "string")
         self.assertEqual(schema["test_field"]["label"], "Test Field")

     def test_save_method_sets_defaults(self):
         """Test save method sets default values correctly"""
         entity = Entity(name="Save Test", url_path="/api/save-test", model_path="auth.User")
         entity.save()
         self.assertIn("title", entity.meta)
         self.assertIn("title", entity.form)
         self.assertEqual(entity.form["title"], "Save Test Form")

     def test_get_options_response(self):
         """Test get_options_response generates the expected response"""
         absolute_url = "https://example.com/api/test-entity"
         response = self.entity.get_options_response(absolute_url)
         self.assertEqual(response["meta"], self.entity.meta)
         self.assertEqual(response["form"]["entity"], absolute_url)
         self.assertEqual(response["layout"][0]["entity"], absolute_url)






# from django.test import TestCase
# from core.models import Entity, BaseModel
# from organization.models import Organization
# from django.apps import apps
# from django.core.exceptions import ImproperlyConfigured
# from core.models import BaseModel
# from django.db import models


# class BaseModelTest(TestCase):
#     def test_base_model(self):
#         base_model_instance = BaseModel()
#         self.assertIsNone(base_model_instance.id)
#         self.assertTrue(hasattr(base_model_instance, 'created_at'))
#         self.assertTrue(hasattr(base_model_instance, 'updated_at'))






# class EntityTest(TestCase):
#     def setUp(self):
#         self.entity = Entity.objects.create(
#             name="Test Entity",
#             url_path="/api/test-entity",
#             model_path="organization.Organization",
#             meta={"title": "Test Title"},
#             form={"title": "Test Form"},
#             actions={},
#             table={},
#             layout=[],
#             permissions=[],
#             POST={},
#             post_heading={"type": "heading_dynamic", "headingType": "h2", "label": "Test Heading"},
#             post_description={"type": "description", "description": "Test Description"},
#             extra_field={"key": "value"},
#             extra_parameter={"param": "value"},
#             post_tabs={"setup_organizations": ["organization_name"]},
#             post_order=["organization_name"],
#         )

#     def test_string_representation(self):
#         self.assertEqual(str(self.entity), "Test Entity - /api/test-entity")

#     def test_get_model_class(self):
#         model_class = self.entity.get_model_class()
#         self.assertEqual(model_class, Organization)

#     def test_get_model_class_invalid(self):
#         self.entity.model_path = "invalid.Model"
#         with self.assertRaises(ImproperlyConfigured):
#             self.entity.get_model_class()

#     def test_build_post_schema(self):
#         schema = self.entity.build_post_schema()
#         self.assertIn("heading", schema)
#         self.assertIn("description", schema)

#     def test_save_method(self):
#         self.entity.save()
#         self.assertIn("title", self.entity.meta)
#         self.assertIn("title", self.entity.form)

#     def test_get_options_response(self):
#         response = self.entity.get_options_response("http://localhost/api/test-entity")
#         self.assertIn("meta", response)
#         self.assertIn("form", response)
#         self.assertIn("actions", response)
#         self.assertIn("POST", response)
