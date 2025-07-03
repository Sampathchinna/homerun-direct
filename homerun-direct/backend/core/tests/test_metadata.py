from django.test import TestCase, RequestFactory
from unittest.mock import MagicMock, patch
from core.models import Entity
from core.metadata import CustomUIMetadata


class CustomUIMetadataTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = MagicMock()
        self.view.get_serializer = MagicMock()
        self.metadata = CustomUIMetadata()

    def test_inject_tab_in_post_fields(self):
        entity = MagicMock()
        entity.post_tabs = {
            "general": ["name", "email"],
            "setup_organizations": ["organization_name"]
        }
        post_response = {
            "name": {},
            "email": {},
            "organization_name": {}
        }

        result = self.metadata.inject_tab_in_post_fields(entity, post_response)

        self.assertEqual(result["name"]["tab"], "general")
        self.assertEqual(result["email"]["tab"], "general")
        self.assertEqual(result["organization_name"]["tab"], "setup_organizations")

    @patch("rbac.models.Entity.objects.get")
    def test_determine_metadata_entity_exists(self, mock_get):
        mock_entity = MagicMock()
        mock_entity.POST = {"field1": {"label": "Field 1"}}
        mock_entity.post_heading = "Post Heading"
        mock_entity.post_description = "Post Description"
        mock_entity.extra_field = {"extra1": "value1"}
        mock_entity.extra_parameter = {"field1": {"placeholder": "Enter text"}}
        mock_entity.post_order = ["field1", {"custom_block": "block_value"}]
        mock_entity.layout = [{"block": "layout_block"}]
        mock_entity.meta = {"title": "Entity Meta"}
        mock_entity.form = {"title": "Entity Form"}
        mock_entity.actions = {"POST": "Entity Actions"}
        mock_entity.permissions = ["view", "edit"]
        mock_entity.table = "Entity Table"
        mock_get.return_value = mock_entity

        request = self.factory.get('/test-path')
        response = self.metadata.determine_metadata(request, self.view)

        self.assertIn("meta", response)
        self.assertIn("form", response)
        self.assertIn("POST", response)
        self.assertIn("layout", response)
        self.assertIn("permissions", response)
        self.assertIn("table", response)

    @patch("rbac.models.Entity.objects.get")
    def test_determine_metadata_entity_does_not_exist(self, mock_get):
        mock_get.side_effect = Entity.DoesNotExist
        request = self.factory.get('/test-path')
        response = self.metadata.determine_metadata(request, self.view)

        self.assertIn("meta", response)
        self.assertIn("form", response)
        self.assertIn("POST", response)
        self.assertIn("layout", response)
        self.assertIn("permissions", response)

    def test_map_type(self):
        type_mapping = {
            "string": "string",
            "integer": "number",
            "boolean": "checkbox",
            "datetime": "date",
            "field": "select",
            "nested object": "group",
        }
        for field_type, expected_output in type_mapping.items():
            result = self.metadata.map_type({"type": field_type})
            self.assertEqual(result, expected_output)

        result = self.metadata.map_type({"type": "unknown"})
        self.assertEqual(result, "string")  # Default fallback

    def test_get_tab(self):
        self.assertEqual(self.metadata.get_tab("organization_name"), "setup_organizations")
        self.assertEqual(self.metadata.get_tab("address"), "business_location")
        self.assertEqual(self.metadata.get_tab("city"), "business_location")
        self.assertEqual(self.metadata.get_tab("terms"), "terms_of_service")
        self.assertEqual(self.metadata.get_tab("other_field"), "general")


import pytest
from unittest.mock import MagicMock
from rest_framework.test import APIRequestFactory
from core.metadata import CustomUIMetadata
from core.models import Entity
from rest_framework import serializers
from django.test import RequestFactory




@pytest.fixture
def request_factory():
    return APIRequestFactory()

@pytest.fixture
def custom_metadata():
    return CustomUIMetadata()


def test_inject_tab_in_post_fields(custom_metadata):
    entity = MagicMock()
    entity.post_tabs = {
        "tab1": ["field1", "field2"],
        "tab2": ["field3"]
    }

    post_response = {
        "field1": {},
        "field2": {},
        "field3": {},
        "field4": {}
    }

    result = custom_metadata.inject_tab_in_post_fields(entity, post_response)

    assert result["field1"]["tab"] == "tab1"
    assert result["field2"]["tab"] == "tab1"
    assert result["field3"]["tab"] == "tab2"
    assert "tab" not in result["field4"]



@pytest.mark.django_db
def test_determine_metadata_with_existing_entity(custom_metadata, request_factory):
    request = request_factory.get("/fake-url")

    entity = Entity.objects.create(
        url_path="/fake-url",
        POST={"test_field": {"type": "string"}},
        post_heading="Test Heading",
        post_description="Test Description",
        extra_field={"extra_key": "extra_value"},
        extra_parameter={"test_field": {"required": True}},
    )

    view = MagicMock()
    view.get_serializer.return_value = MagicMock(fields={})

    metadata = custom_metadata.determine_metadata(request, view)

    assert metadata["POST"]["test_field"]["required"] is True
    assert metadata["POST"]["heading"] == "Test Heading"
    assert metadata["POST"]["description"] == "Test Description"
    assert metadata["POST"]["extra_key"] == "extra_value"


@pytest.mark.django_db
def test_determine_metadata_with_non_existing_entity(custom_metadata, request_factory):
    request = request_factory.get("/non-existing-url")

    view = MagicMock()
    view.get_serializer.return_value = MagicMock(fields={})

    metadata = custom_metadata.determine_metadata(request, view)

    assert "POST" in metadata
    assert metadata["meta"]["title"] == "New Entity"







def test_build_ui_post(custom_metadata):
    serializer = MagicMock()
    serializer.fields = {
        "name": serializers.CharField(),
        "age": serializers.IntegerField(),
        "gender": serializers.ChoiceField(choices=[("M", "Male"), ("F", "Female")]),
    }

    post_fields = {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "gender": {"type": "field"},
    }

    result = custom_metadata.build_ui_post(post_fields, serializer)

    expected_options = [
        {"label": "Male", "value": "M"},
        {"label": "Female", "value": "F"}
    ]

    # Debugging: Print both expected and actual options to compare
    print("Expected Options:", expected_options)
    print("Actual Options:", result["gender"]["options"])

    # Compare ignoring order and ensuring types match
    assert all(isinstance(option['label'], str) and isinstance(option['value'], str) for option in result["gender"]["options"])
    assert sorted(result["gender"]["options"], key=lambda x: x['value']) == sorted(expected_options, key=lambda x: x['value'])








# from rest_framework.metadata import SimpleMetadata
# from core.models import Entity


# class CustomUIMetadata(SimpleMetadata):
#     def inject_tab_in_post_fields(self, entity, post_response):
#         for tab, fields in entity.post_tabs.items():
#             for field in fields:
#                 if field in post_response:
#                     post_response[field]["tab"] = tab
#         return post_response

#     def determine_metadata(self, request, view):
#         default = super().determine_metadata(request, view)

#         if not hasattr(view, "get_serializer"):
#             return default

#         serializer = view.get_serializer()
#         post_fields = default.get("actions", {}).get("POST", {})
#         ui_post = self.build_ui_post(post_fields, serializer)

#         try:
#             entity = Entity.objects.get(url_path=request.path)
#             post_response = entity.POST or ui_post
#             post_response = self.inject_tab_in_post_fields(entity, post_response)

#             if entity.post_heading:
#                 post_response["heading"] = entity.post_heading
#             if entity.post_description:
#                 post_response["description"] = entity.post_description

#             if entity.extra_field:
#                 if isinstance(entity.extra_field, dict):  # Ensure it's a dictionary
#                     for key, value in entity.extra_field.items():
#                         if key not in post_response:
#                             post_response[key] = (
#                                 value  # Append new keys from extra_field
#                             )

#             # Overwrite only matching Input field properties
#             if entity.extra_parameter:

#                 # Overwrite only matching keys in post_response
#                 for key, value in entity.extra_parameter.items():
#                     if key in post_response and isinstance(post_response[key], dict):
#                         post_response[key].update(value)
#                     else:
#                         post_response[key] = value

#             # Simplified post_order logic
#             ordered_post = []
#             added_keys = set()

#             for item in entity.post_order or []:
#                 if isinstance(item, str) and item in post_response:
#                     ordered_post.append((item, post_response[item]))
#                     added_keys.add(item)
#                 elif isinstance(item, dict):
#                     ordered_post.append(item)

#             for key, value in post_response.items():
#                 if key not in added_keys:
#                     ordered_post.append((key, value))

#             # Convert to final dict
#             final_post = {}
#             i = 0
#             for item in ordered_post:
#                 if isinstance(item, tuple):
#                     final_post[item[0]] = item[1]
#                 elif isinstance(item, dict):
#                     final_post[f"__separator_{i}"] = item
#                     i += 1

#             return {
#                 "meta": entity.meta,
#                 "form": {**entity.form, "entity": request.build_absolute_uri()},
#                 "actions": entity.actions,
#                 "extra_parameter": entity.extra_parameter,
#                 "extra_field": entity.extra_field,
#                 "table": entity.table,
#                 "layout": [
#                     {**block, "entity": request.build_absolute_uri()}
#                     for block in entity.layout
#                 ],
#                 "permissions": entity.permissions,
#                 "POST": final_post,
#                 "post_order": entity.post_order or [],
#             }

#         except Entity.DoesNotExist:
#             return {
#                 "meta": {"title": "New Entity", "description": ""},
#                 "form": {
#                     "title": "Generated Form",
#                     "form_template": "form-template-one",
#                     "input_template": "default",
#                     "entity": request.build_absolute_uri(),
#                     "description": None,
#                     "size": {
#                         "width": 50,
#                         "height": "auto",
#                         "maxWidth": 50,
#                         "maxHeight": 80,
#                     },
#                     "column": {"desktop": 1, "laptop": 1, "tablet": 1},
#                     "gap": 4,
#                 },
#                 "layout": [
#                     {
#                         "template": "default-style",
#                         "url": request.path.replace("/api", ""),
#                         "entity": request.build_absolute_uri(),
#                         "api": [],
#                     }
#                 ],
#                 "permissions": [],
#                 "POST": ui_post,
#             }

#     def build_ui_post(self, post_fields, serializer):
#         ui_post = {}
#         for field_name, field_info in post_fields.items():
#             new_field = {
#                 "type": self.map_type(field_info),
#                 "label": field_info.get("label", field_name.replace("_", " ").title()),
#                 "read_only": field_info.get("read_only", False),
#                 "required": field_info.get("required", False),
#                 "tab": self.get_tab(field_name),
#                 "max_length": field_info.get("max_length", 100),
#                 "label_hidden": True,
#                 "placeholder": "",
#                 "column_class_name": "mb-4 space-y-1",
#             }

#             field = serializer.fields.get(field_name)

#             if hasattr(field, "choices") and isinstance(field.choices, dict):
#                 new_field["type"] = "select"
#                 new_field["options"] = [
#                     {"label": str(label), "value": value}
#                     for value, label in field.choices.items()
#                 ]
#                 new_field["bindLabel"] = "label"
#                 new_field["bindValue"] = "value"

#             elif hasattr(field, "queryset") and field.queryset is not None:
#                 model = field.queryset.model
#                 new_field["type"] = "select"

#                 def get_label_value(obj):
#                     if hasattr(obj, "label") and hasattr(obj, "value"):
#                         return {"label": obj.label, "value": obj.value}
#                     else:
#                         return {"label": str(obj), "value": obj.pk}

#                 new_field["options"] = [
#                     get_label_value(obj) for obj in model.objects.all()
#                 ]
#                 new_field["bindLabel"] = "label"
#                 new_field["bindValue"] = "value"

#             ui_post[field_name] = new_field
#         return ui_post

#     def map_type(self, field_info):
#         return {
#             "string": "string",
#             "integer": "number",
#             "boolean": "checkbox",
#             "datetime": "date",
#             "field": "select",
#             "nested object": "group",
#         }.get(field_info.get("type", "string"), "string")

#     def get_tab(self, field_name):
#         if "organization" in field_name:
#             return "setup_organizations"
#         elif "address" in field_name or "city" in field_name:
#             return "business_location"
#         elif "terms" in field_name:
#             return "terms_of_service"
#         return "general"
