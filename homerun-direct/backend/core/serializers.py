from rest_framework import serializers
from django.core.exceptions import ValidationError

class GenericSerializer(serializers.ModelSerializer):
    """A Generic Model Serializer with overridden create and update methods"""

    def create(self, validated_data):
        """Override create method for custom logic and validation"""
        print("Validated Data:", validated_data)  # Debugging without stopping tests

        instance = self.Meta.model(**validated_data)  # Create instance but don't save yet
        try:
            instance.full_clean()  # Calls model.clean() for validation
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)  # Convert to DRF validation error

        instance.save()
        return instance

    def update(self, instance, validated_data):
        """Override update method for custom logic and validation"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        try:
            instance.full_clean()  # Calls model.clean() for validation
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)  # Convert to DRF validation error

        instance.save()
        return instance

    class Meta:
        model = None  # This must be set dynamically in subclasses
        fields = "__all__"  # Override in child classes
