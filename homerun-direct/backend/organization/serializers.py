from core.serializers import GenericSerializer
from rest_framework import serializers
from .models import Organization
from master.models import Location,LocationableType
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from organization.cache_utils import update_cache
from .models import Brand
from rest_framework.request import Request
from rest_framework import serializers
from .models import (
    Brand,
    BrandFooters,
    BrandHeaders,
    BrandHomePages,
    BrandInfos,
    BrandPages,
    BrandPageSliceHeadline,
    BrandPageSliceAmenities,
    BrandPageSliceFeaturedListings,
    BrandPageSliceGridContentBlocks,
    BrandPageSliceHeadline,
    BrandPageSliceHomepageHeros,
    BrandPageSliceLocalActivities,
    BrandPageSliceMediaContentBlocks,
    BrandPageSlicePhotoGalleries,
    BrandPageSlicePullQuotes,
    BrandPageSliceReviews,
    BrandPageSliceSingleImages,
    BrandPageSliceVideoEmbeds,
    BrandPageSlices,
    BrandsEmployees,
)


class OrganizationSerializer(GenericSerializer):
    # ✅ Flat input fields instead of "location"
    street_address = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    apt_suite = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    city = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    state_province = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    postal_code = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    country = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    latitude = serializers.DecimalField(write_only=True, required=False, allow_null=True, max_digits=12, decimal_places=9)
    longitude = serializers.DecimalField(write_only=True, required=False, allow_null=True, max_digits=12, decimal_places=9)


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.location:
            rep.update({
                "street_address": instance.location.street_address,
                "apt_suite": instance.location.apt_suite,
                "city": instance.location.city,
                "state_province": instance.location.state_province,
                "postal_code": instance.location.postal_code,
                "country": instance.location.country,
                "latitude": instance.location.latitude,
                "longitude": instance.location.longitude,
            })
        return rep

    # ✅ Extra response fields
    subscription_plan_id = serializers.IntegerField(source="subscription_plan.id", read_only=True)
    organization_id = serializers.IntegerField(source="id", read_only=True)
    # ✅ Disable user and  locations

    user = serializers.SerializerMethodField(read_only=True)  # will show in response, not required in form input
    def get_user(self, obj):
        return obj.user.id if obj.user else None

    location = serializers.PrimaryKeyRelatedField(read_only=True)  # 👈 explicitly disable

    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ['is_organization_created']
        extra_kwargs = {
            "location": {"required": False},
            "user": {"required": False, "allow_null": True},
            "organization_type": {"required": False, "allow_null": True},
            "language": {"required": False, "allow_null": True},
            "currency": {"required": False, "allow_null": True},
            "company_type": {"required": False, "allow_null": True},
            "payment_processor": {"required": False, "allow_null": True},
        }

    def create(self, validated_data):
        # Extract location data
        validated_data['user'] = self.context['request'].user
        validated_data['is_organization_created'] = True
        location_data = {field: validated_data.pop(field, None) for field in [
            "street_address", "apt_suite", "city", "state_province",
            "postal_code", "country", "latitude", "longitude"
        ]}

        locationable_type, _ = LocationableType.objects.get_or_create(name="Organization")
        # ✅ Get or create location (now includes postal_code, country, latitude, longitude)
        location, created = Location.objects.get_or_create(
            city=location_data["city"],
            state_province=location_data["state_province"],
            country=location_data["country"],
            postal_code=location_data["postal_code"],
            latitude=location_data["latitude"],
            longitude=location_data["longitude"],
            defaults={
                    **location_data,
                    "locationable_type": locationable_type,
                }
        )

        validated_data["location"] = location

        organization = super().create(validated_data)

        # Store organization ID in the session
        session = self.context['request'].session
        organization_ids = session.get("organization_ids", [])
        if organization.id not in organization_ids:
            organization_ids.append(organization.id)
            session["organization_ids"] = organization_ids
            session.modified = True  # Mark session as changed

        return organization

    def update(self, instance, validated_data):
        request = self.context.get("request")
        is_partial = request.method == "PATCH" if isinstance(request, Request) else False
        location_data = {field: validated_data.pop(field, None) for field in [
            "street_address", "apt_suite", "city", "state_province", "postal_code", "country", "latitude", "longitude"
        ]}
        
        locationable_type, _ = LocationableType.objects.get_or_create(name="Organization")
        
        if instance.location:
            for key, val in location_data.items():
                if val is not None:
                    setattr(instance.location, key, val)
            instance.location.locationable_type = locationable_type  # Ensure not null
            instance.location.save()

        elif any(location_data.values()):
            location, created = Location.objects.get_or_create(
                city=location_data["city"],
                state_province=location_data["state_province"],
                country=location_data["country"],
                postal_code=location_data["postal_code"],
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                defaults={**location_data, "locationable_type": locationable_type}
            )
            if not created:
                location.locationable_type = locationable_type
                location.save()
            validated_data["location"] = location

        # Manually update other fields (e.g., organization_type, user)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        try:
            instance.full_clean(validate_unique=not is_partial)
        except ValidationError as e:
            raise serializers.ValidationError({"error": e.message_dict})

        instance.save()
        return instance



    def validate(self, attrs):
        if not attrs.get("terms_agreement"):
            raise serializers.ValidationError({"terms_agreement": "You must agree to terms to proceed."})
        return attrs





class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

    def create(self, validated_data):
        # Create the Brand instance
        brand = super().create(validated_data)

        # Attach its ID to the session
        request = self.context.get('request')
        if request:
            session = request.session
            brand_ids = session.get("brand_ids", [])
            if brand.id not in brand_ids:
                brand_ids.append(brand.id)
                session["brand_ids"] = brand_ids
                session.modified = True

        return brand    # ← make sure to return the created instance!


class BrandFootersSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandFooters
        fields = '__all__'


class BrandHeadersSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandHeaders
        fields = '__all__'


class BrandHomePagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandHomePages
        fields = '__all__'


class BrandInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandInfos
        fields = '__all__'


class BrandPagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPages
        fields = '__all__'


class BrandPageSliceHeadlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceHeadline
        fields = '__all__'


class BrandPageSliceAmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceAmenities
        fields = '__all__'


class BrandPageSliceFeaturedListingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceFeaturedListings
        fields = '__all__'


class BrandPageSliceGridContentBlocksSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceGridContentBlocks
        fields = '__all__'


class BrandPageSliceHeadlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceHeadline
        fields = '__all__'


class BrandPageSliceHomepageHerosSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceHomepageHeros
        fields = '__all__'


class BrandPageSliceLocalActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceLocalActivities
        fields = '__all__'


class BrandPageSliceMediaContentBlocksSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceMediaContentBlocks
        fields = '__all__'


class BrandPageSlicePhotoGalleriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSlicePhotoGalleries
        fields = '__all__'


class BrandPageSlicePullQuotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSlicePullQuotes
        fields = '__all__'


class BrandPageSliceReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceReviews
        fields = '__all__'


class BrandPageSliceSingleImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceSingleImages
        fields = '__all__'


class BrandPageSliceVideoEmbedsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSliceVideoEmbeds
        fields = '__all__'


class BrandPageSlicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPageSlices
        fields = '__all__'


class BrandsEmployeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandsEmployees
        fields = '__all__'