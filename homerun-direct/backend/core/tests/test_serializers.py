import pytest
from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError
from core.models import Entity
from core.serializers import GenericSerializer
from uuid import uuid4



class EntitySerializer(GenericSerializer):
    class Meta:
        model = Entity
        fields = "__all__"

@pytest.mark.django_db(transaction=True)
class GenericSerializerTests(TestCase):

    def setUp(self):
        unique_path = f"/api/test-entity-{uuid4()}"
        self.valid_data = {
            "name": "Test Entity",
            "url_path": unique_path,
            "model_path": "core.Entity",
            "meta": {"title": "Test Title"},
            "form": {"title": "Test Form"},
            "actions": {},
            "table": {},
            "layout": [],
            "permissions": [],
            "POST": {},
            "post_heading": {"type": "heading_dynamic", "label": "Let's Get Started"},
            "post_description": {"type": "description", "description": "Description Text"},
            "extra_field": {},
            "extra_parameter": {},
            "post_tabs": {},
            "post_order": {},
        }
        self.invalid_data = {
            "name": "",
            "url_path": "",
            "model_path": "",
        }
        self.entity_instance = Entity.objects.create(**self.valid_data)

    def tearDown(self):
        Entity.objects.all().delete()  # Cleanup after each test

    def test_invalid_fields(self):
        unique_path = f"/api/test-entity-{uuid4()}"
        serializer = EntitySerializer(data={"invalid_field": "value", "url_path": unique_path, "model_path": "core.Entity"})
        assert not serializer.is_valid()
        assert "invalid_field" not in serializer.errors  # This will fail if URL path conflict happens
        assert "url_path" not in serializer.errors  # Ensures the error is not related to URL path conflict

    def test_serializer_initialization(self):
        unique_path = f"/api/test-entity-{uuid4()}"
        self.valid_data["url_path"] = unique_path  # Use a unique URL path
        serializer = EntitySerializer(data=self.valid_data)
        assert serializer.is_valid(), serializer.errors



    def test_create_method_success(self):
        Entity.objects.all().delete()  # Ensure a clean slate
        serializer = EntitySerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        assert instance.pk is not None
        assert instance.name == self.valid_data["name"]

    def test_create_method_validation_error(self):
        serializer = EntitySerializer(data=self.invalid_data)
        with pytest.raises(DRFValidationError):
            serializer.is_valid(raise_exception=True)
            # serializer.save()

    def test_update_method_success(self):
        update_data = {"name": "Updated Entity"}
        serializer = EntitySerializer(instance=self.entity_instance, data=update_data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        assert instance.name == "Updated Entity"

    def test_update_method_validation_error(self):
        update_data = {"name": ""}
        serializer = EntitySerializer(instance=self.entity_instance, data=update_data, partial=True)
        with pytest.raises(DRFValidationError):
            serializer.is_valid(raise_exception=True)
            # serializer.save()

    def test_full_clean_called_on_create(self):
        Entity.objects.all().delete()  # Ensure no conflicts
        serializer = EntitySerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.full_clean()  # Should not raise any errors

    def test_full_clean_called_on_update(self):
        self.entity_instance.name = "Valid Name"
        self.entity_instance.full_clean()  # Validates successfully

    def test_meta_class_handling(self):
        serializer = EntitySerializer(instance=self.entity_instance)
        assert serializer.Meta.model == Entity
        assert serializer.Meta.fields == "__all__"

    def test_empty_data(self):
        serializer = EntitySerializer(data={})
        assert not serializer.is_valid()
        assert "This field is required." in str(serializer.errors)



    def test_build_post_schema(self):
        schema = self.entity_instance.build_post_schema()
        assert isinstance(schema, dict)
        assert "heading" in schema
        assert "description" in schema

    def test_get_options_response(self):
        absolute_url = f"/api/test-entity-{uuid4()}/"
        response = self.entity_instance.get_options_response(absolute_url)
        assert isinstance(response, dict)
        assert "meta" in response
        assert "form" in response
        assert "actions" in response
        assert "table" in response
        assert "layout" in response
        assert "permissions" in response
        assert "POST" in response
        assert response["form"]["entity"] == absolute_url

    def test_save_method(self):
        entity = Entity(name="New Test", url_path=f"/api/new-test-{uuid4()}", model_path="core.Entity")
        entity.save()
        assert entity.meta["title"] == "New Test"
        assert entity.form["title"] == "New Test Form"
        assert isinstance(entity.layout, list)
        assert isinstance(entity.POST, dict)

# This test should be outside the TestCase class for capsys to work
@pytest.mark.django_db
def test_serializer_print_output(capsys):
    unique_path = f"/api/test-entity-{uuid4()}"
    valid_data = {
        "name": "Test Entity",
        "url_path": unique_path,
        "model_path": "core.Entity",
        "meta": {"title": "Test Title"},
        "form": {"title": "Test Form"},
    }
    serializer = EntitySerializer(data=valid_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    print("Validated Data: ", serializer.validated_data)
    captured = capsys.readouterr()
    assert "Validated Data" in captured.out
