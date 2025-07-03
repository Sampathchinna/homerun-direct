from rest_framework import serializers
class FKNestedSaveMixin:
    nested_fk_map = {}
    required_nested_fields = []  # You can now ignore this if not enforcing

    def handle_nested_foreign_keys(self, validated_data, instance=None):
        for field, model_cls in self.nested_fk_map.items():
            data = validated_data.pop(field, None)

            # ✅ If valid dict with non-empty values, proceed
            if isinstance(data, dict) and any(data.values()):
                if instance and getattr(instance, field, None):
                    related_obj = getattr(instance, field)
                    for attr, val in data.items():
                        setattr(related_obj, attr, val)
                    related_obj.save()
                    validated_data[field] = related_obj
                else:
                    related_obj = model_cls.objects.create(**data)
                    validated_data[field] = related_obj
