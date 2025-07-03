from rest_framework import serializers
from core.serializers import GenericSerializer
from organization.models import Organization
from rest_framework import serializers
from .models import *
from rest_framework.exceptions import ValidationError
from rbac.models import OrganizationProperty


class ReservationSerializer(GenericSerializer):
    #organization_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = ReservationNew
        fields = '__all__'

    def create(self, validated_data):
        instance = ReservationNew(**validated_data)
        instance.full_clean()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance


class ReservationInformationSerializer(GenericSerializer):
    #id = serializers.IntegerField(read_only=True)
    class Meta:
        model = ReservationInformation
        fields = '__all__'


class FeeLineItemSerializer(GenericSerializer):
    owner_split_id    = serializers.IntegerField(write_only=True, allow_null=True)
    #id                = serializers.IntegerField(read_only=True)

    class Meta:
        model = LineItemFee
        fields = '__all__'

    def create(self, validated_data):
        os_ = validated_data.pop('owner_split_id', None)
        if os_:validated_data['owner_split']    = OwnerSplit.objects.get(pk=os_)
        return super().create(validated_data)


class TaxAccountsSerializer(GenericSerializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    
    class Meta:
        model = TaxAccounts
        fields = '__all__'
    def create(self, validated_data):
        q = validated_data.pop('organization_id')
        if ca: validated_data['organization_id'] = Organization.objects.get(pk=q)
        return super().create(validated_data)

class TaxLineItemSerializer(GenericSerializer):
    quote_id          = serializers.IntegerField(write_only=True)
    credit_account_id = serializers.IntegerField(write_only=True, allow_null=True)
    debit_account_id  = serializers.IntegerField(write_only=True, allow_null=True)
    owner_split_id    = serializers.IntegerField(write_only=True, allow_null=True)
    #id                = serializers.IntegerField(read_only=True)

    class Meta:
        model = LineItemTax
        fields = '__all__'

    def create(self, validated_data):
        q = validated_data.pop('quote_id')
        ca = validated_data.pop('credit_account_id', None)
        da = validated_data.pop('debit_account_id', None)
        os_ = validated_data.pop('owner_split_id', None)
        validated_data['quote']          = Quote.objects.get(pk=q)
        if ca: validated_data['credit_account'] = CreditAccount.objects.get(pk=ca)
        if da: validated_data['debit_account']  = DebitAccount.objects.get(pk=da)
        if os_:validated_data['owner_split']    = OwnerSplit.objects.get(pk=os_)
        return super().create(validated_data)


class PropertyListingSerializer(GenericSerializer):
    unit_listing_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PropertyListing
        fields = '__all__'

    def create(self, validated_data):
        ul = validated_data.pop('unit_listing_id')
        validated_data['unit_listing'] = UnitListing.objects.get(pk=ul)
        return super().create(validated_data)


class UnitListingSerializer(GenericSerializer):
    brand_id  = serializers.IntegerField(write_only=True)

    class Meta:
        model = UnitListing
        fields = '__all__'

    def create(self, validated_data):
        b = validated_data.pop('brand_id')
        from branding.models import Brand
        validated_data['brand'] = Brand.objects.get(pk=b)
        return super().create(validated_data)


class CustomerInformationSerializer(GenericSerializer):
    booking_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CustomerInformation
        fields = '__all__'

    def create(self, validated_data):
        bid = validated_data.pop('booking_id')
        validated_data['booking_id'] = ReservationNew.objects.get(id=bid)
        return super().create(validated_data)


class ChargeSerializer(GenericSerializer):

    class Meta:
        model = Charge
        fields = '__all__'


class PaymentMethodSerializer(GenericSerializer):

    class Meta:
        model = PaymentMethod
        fields = '__all__'


class NoteSerializer(GenericSerializer):

    class Meta:
        model = Note
        fields = '__all__'



class WorkOrderSerializer(GenericSerializer):
    unit = serializers.PrimaryKeyRelatedField(queryset=Units.objects.all(), required=False)
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(), required=False)
    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all(), required=False)

    class Meta:
        model = WorkOrder
        fields = '__all__'



class WorkReportSerializer(GenericSerializer):
    
    class Meta:
        model = WorkReport
        fields = '__all__'

    def validate(self, attrs):
        """
        Validate that the WorkOrder exists and is active or valid.
        """
        work_order = attrs.get('work_order')
        if not work_order or not isinstance(work_order, WorkOrder):
            raise serializers.ValidationError("Invalid WorkOrder provided.")
        return attrs


class InternetOptionsSerializer(GenericSerializer):
    property_id = serializers.IntegerField(write_only=True)
    organization_id = serializers.IntegerField(write_only=True)
    #id = serializers.IntegerField(read_only=True)

    class Meta:
        model = InternetOptions
        fields = '__all__'
        extra_kwargs = {
            'property': {'read_only': True},
            'organization': {'read_only': True},
        }

    def create(self, validated_data):
        pid = validated_data.pop('property_id')
        oid = validated_data.pop('organization_id')
        validated_data['property'] = Property.objects.get(pk=pid)
        validated_data['organization'] = Organization.objects.get(pk=oid)
        instance=InternetOptions(**validated_data)
        instance.full_clean()
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        prop_id = validated_data.pop('property_id', None)
        if prop_id:
            validated_data['property'] = Property.objects.get(pk=prop_id)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance


class BedroomsBathroomsSerializer(GenericSerializer):
    unit_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BedroomsBathrooms
        fields = '__all__'
        extra_kwargs = {
            'unit': {'read_only': True},
        }

    def create(self, validated_data):
        uid = validated_data.pop('unit_id')
        validated_data['unit'] = Units.objects.get(pk=uid)
        instance=BedroomsBathrooms(**validated_data)
        instance.full_clean()
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        uid = validated_data.pop('unit_id', None)
        if uid is not None:
            try:
                instance.unit = Units.objects.get(pk=uid)
            except Units.DoesNotExist:
                raise serializers.ValidationError({"unit_id": "Unit with this ID does not exist."}) 
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance

class BedroomsSerializer(GenericSerializer):
    unit_id = serializers.IntegerField(write_only=True)
    bedrooms_bathrooms_id = serializers.IntegerField(write_only=True)
    organization_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Bedrooms
        fields = '__all__'
        extra_kwargs = {
            'unit': {'read_only': True},
            'bedrooms_bathrooms': {'read_only': True},
            'organization': {'read_only': True},
        }

    def create(self, validated_data):
        uid = validated_data.pop('unit_id')
        bbid = validated_data.pop('bedrooms_bathrooms_id')
        oid = validated_data.pop('organization_id')
        validated_data['unit'] = Units.objects.get(pk=uid)
        validated_data['bedrooms_bathrooms'] = BedroomsBathrooms.objects.get(pk=bbid)
        validated_data['organization'] = Organization.objects.get(pk=oid)
        return super().create(validated_data)

class LivingRoomsSerializer(GenericSerializer):
    unit_id = serializers.IntegerField(write_only=True)
    bedrooms_bathrooms_id = serializers.IntegerField(write_only=True)
    organization_id = serializers.IntegerField(write_only=True)
    #id = serializers.IntegerField(read_only=True)

    class Meta:
        model = LivingRooms
        fields = '__all__'
        extra_kwargs = {
            'unit': {'read_only': True},
            'bedrooms_bathrooms': {'read_only': True},
            'organization': {'read_only': True},
        }

    def create(self, validated_data):
        uid = validated_data.pop('unit_id')
        bbid = validated_data.pop('bedrooms_bathrooms_id')
        oid = validated_data.pop('organization_id')
        validated_data['unit'] = Units.objects.get(pk=uid)
        validated_data['bedrooms_bathrooms'] = BedroomsBathrooms.objects.get(pk=bbid)
        validated_data['organization'] = Organization.objects.get(pk=oid)
        return super().create(validated_data)

class BathroomSerializer(GenericSerializer):
    unit_id = serializers.IntegerField(write_only=True)
    bedrooms_bathrooms_id = serializers.IntegerField(write_only=True)
    organization_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Bathroom
        fields = '__all__'
        extra_kwargs = {
            'unit': {'read_only': True},
            'bedrooms_bathrooms': {'read_only': True},
            'organization': {'read_only': True},
        }

    def create(self, validated_data):
        uid = validated_data.pop('unit_id')
        bbid = validated_data.pop('bedrooms_bathrooms_id')
        oid = validated_data.pop('organization_id')
        validated_data['unit'] = Units.objects.get(pk=uid)
        validated_data['bedrooms_bathrooms'] = BedroomsBathrooms.objects.get(pk=bbid)
        validated_data['organization'] = Organization.objects.get(pk=oid)
        return super().create(validated_data)

class AvailabilitySerializer(GenericSerializer):
    unit_id = serializers.IntegerField(write_only=True)
    organization_id = serializers.IntegerField(write_only=True)
    #id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Availability
        fields = '__all__'
        extra_kwargs = {
            'unit': {'read_only': True},
            'organization': {'read_only': True},
        }

    def create(self, validated_data):
        uid = validated_data.pop('unit_id')
        oid = validated_data.pop('organization_id')
        validated_data['unit'] = Units.objects.get(pk=uid)
        validated_data['organization'] = Organization.objects.get(pk=oid)
        return super().create(validated_data)

class PricingSerializer(GenericSerializer):
    unit_id = serializers.IntegerField(write_only=True)
    organization_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Pricing
        fields = '__all__'
        extra_kwargs = {
            'unit': {'read_only': True},
            'organization': {'read_only': True},
        }

    def create(self, validated_data):
        uid = validated_data.pop('unit_id')
        oid = validated_data.pop('organization_id')
        validated_data['unit'] = Units.objects.get(pk=uid)
        validated_data['organization'] = Organization.objects.get(pk=oid)
        instance=Pricing(**validated_data)
        instance.full_clean()
        instance.save()
        return instance
    def update(self, instance, validated_data):
        uid = validated_data.pop('unit_id', None)
        oid = validated_data.pop('organization_id', None)
        if uid:
            validated_data['unit'] = Units.objects.get(pk=uid)
        if oid:
            validated_data['organization'] = Organization.objects.get(pk=oid)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance

   


class DepositsSerializer(GenericSerializer):
    organization_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Deposits
        fields = '__all__'
        extra_kwargs = {
            'organization': {'read_only': True},
        }

    def create(self, validated_data):
        oid = validated_data.pop('organization_id')
        validated_data['organization'] = Organization.objects.get(pk=oid)
        return super().create(validated_data)

class FeeAccountsSerializer(GenericSerializer):
    organization_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FeeAccounts
        fields = '__all__'
        extra_kwargs = {
            'organization': {'read_only': True},
        }

    def create(self, validated_data):
        oid = validated_data.pop('organization_id')
        validated_data['organization'] = Organization.objects.get(pk=oid)
        instance=FeeAccounts(**validated_data)
        instance.full_clean()
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        oid = validated_data.pop('organization_id', None)
        if oid is not None:
            try:
                instance.organization = Organization.objects.get(pk=oid)
            except Organization.DoesNotExist:
                raise serializers.ValidationError({"organization_id": "Unit with this ID does not exist."}) 
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance


class DebitAccountSerializer(GenericSerializer):

    class Meta:
        model = DebitAccount
        fields = '__all__'

class CreditAccountSerializer(GenericSerializer):

    class Meta:
        model = CreditAccount
        fields = '__all__'

class RefundPoliciesSerializer(GenericSerializer):

    class Meta:
        model = RefundPolicies
        fields = '__all__'

class UnitsSerializer(GenericSerializer):
    property_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Units
        fields = '__all__'
        extra_kwargs = {'property': {'read_only': True}}

    def create(self, validated_data):
        pid = validated_data.pop('property_id')
        validated_data['property'] = Property.objects.get(pk=pid)
        instance= Units(**validated_data)
        instance.full_clean()
        instance.save()
        return instance
        
    def update(self, instance, validated_data):
        pid = validated_data.pop('property_id', None)
        if pid:
            validated_data['property'] = Property.objects.get(pk=pid)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance


class PropertySerializer(GenericSerializer):
    organization_id = serializers.IntegerField(write_only=True)
    property_type_id = serializers.IntegerField(write_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Property
        fields = '__all__'
        extra_kwargs = {
            'extra': {'required': False},
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Add organization_id from the OrganizationProperty link (if exists)
        org_prop = OrganizationProperty.objects.filter(property=instance).first()
        rep["organization_id"] = (
            org_prop.organization.id
            if org_prop else instance.organization.id if instance.organization else None
        )

        # Include property_type_id in the output
        rep["property_type_id"] = instance.property_type.id if instance.property_type else None

        return rep

    def create(self, validated_data):
        org_id = validated_data.pop('organization_id')
        property_type_id = validated_data.pop('property_type_id')

        organization = Organization.objects.get(id=org_id)
        property_type = PropertyType.objects.get(id=property_type_id)

        validated_data['organization'] = organization
        validated_data['property_type'] = property_type

        instance = Property(**validated_data)
        instance.full_clean()
        instance.save()

        OrganizationProperty.objects.create(
            organization=organization,
            property=instance
        )
        return instance

    def update(self, instance, validated_data):
        org_id = validated_data.pop("organization_id", None)
        property_type_id = validated_data.pop("property_type_id", None)
        if org_id:
            organization = Organization.objects.get(id=org_id)
            instance.organization = organization

        if property_type_id:
            property_type = PropertyType.objects.get(id=property_type_id)
            instance.property_type = property_type

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.full_clean()
        instance.save()

        if org_id:
            OrganizationProperty.objects.update_or_create(
                property=instance,
                defaults={'organization': organization}
            )
        return instance

class ImagesPropertySerializer(GenericSerializer):
    property_id = serializers.IntegerField(write_only=True)
    organization_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ImagesProperty
        fields = '__all__'
        extra_kwargs = {
            'property': {'read_only': True},
            'organization': {'read_only': True},
        }

    def create(self, validated_data):
        # Extract IDs
        prop_id = validated_data.pop('property_id')
        org_id = validated_data.pop('organization_id')

        # Get related instances safely
        try:
            property_instance = Property.objects.get(pk=prop_id)
        except Property.DoesNotExist:
            raise serializers.ValidationError({'property_id': 'Invalid property ID.'})

        try:
            organization_instance = Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError({'organization_id': 'Invalid organization ID.'})

        # Assign foreign key instances
        validated_data['property'] = property_instance
        validated_data['organization'] = organization_instance

        # Create and validate instance
        instance = ImagesProperty(**validated_data)
        instance.full_clean()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # Optional foreign key updates
        prop_id = validated_data.pop('property_id', None)
        org_id = validated_data.pop('organization_id', None)

        if prop_id:
            try:
                validated_data['property'] = Property.objects.get(pk=prop_id)
            except Property.DoesNotExist:
                raise serializers.ValidationError({'property_id': 'Invalid property ID.'})

        if org_id:
            try:
                validated_data['organization'] = Organization.objects.get(pk=org_id)
            except Organization.DoesNotExist:
                raise serializers.ValidationError({'organization_id': 'Invalid organization ID.'})

        # Update model instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.full_clean()
        instance.save()
        return instance

    def to_representation(self, instance):
        """Optional: Include `property_id` and `organization_id` in the response"""
        rep = super().to_representation(instance)
        rep['property_id'] = instance.property.id if instance.property else None
        rep['organization_id'] = instance.organization.id if instance.organization else None
        return rep

class PropertyLocationSerializer(GenericSerializer):
    # Flat input for FK
    property_id = serializers.IntegerField(write_only=True)
    location_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PropertyLocation
        fields = '__all__'
        extra_kwargs = {
            'property': {'read_only': True},
            'location': {'read_only': True},
        }

    def create(self, validated_data):
        prop_id = validated_data.pop('property_id')
        org_id = validated_data.pop('location_id')
        validated_data['property'] = Property.objects.get(pk=prop_id)
        validated_data['location'] = Location.objects.get(pk=org_id)
        return super().create(validated_data)


    def update(self, instance, validated_data):
        prop_id = validated_data.pop('property_id', None)
        if prop_id:
            validated_data['property'] = Property.objects.get(pk=prop_id)
        loc_id = validated_data.pop('location_id', None)
        if loc_id:
            validated_data['location'] = Location.objects.get(pk=loc_id)        
        # Now safely update the rest
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class GuestControlsSerializer(GenericSerializer):
    property_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = GuestControls
        fields = '__all__'
        extra_kwargs = {
            'property': {'read_only': True},
        }

    def create(self, validated_data):
        prop_id = validated_data.pop('property_id')
        validated_data['property'] = Property.objects.get(pk=prop_id)
        instance = GuestControls(**validated_data)
        instance.full_clean()
        instance.save()
        return instance
        
    def update(self, instance, validated_data):
        prop_id = validated_data.pop('property_id', None)
        if prop_id:
            validated_data['property'] = Property.objects.get(pk=prop_id)
        
        # Now safely update the rest
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance

class DeductionAccountsSerializer(GenericSerializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())

    class Meta:
        model = DeductionAccounts
        fields = '__all__'

    def create(self, validated_data):
        organization_id = validated_data.pop('organization_id')
        validated_data['organization'] = Organization.objects.get(pk=organization_id)
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        organization_id = validated_data.pop('organization_id', None)
        if organization_id:
            validated_data['organization'] = Organization.objects.get(pk=organization_id)
        
        # Now safely update the rest
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class InventoryItemSerializer(GenericSerializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())

    class Meta:
        model = InventoryItem
        fields = '__all__'

    def create(self, validated_data):
        organization_id = validated_data.pop('organization_id')
        validated_data['organization'] = Organization.objects.get(pk=organization_id)
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        organization_id = validated_data.pop('organization_id', None)
        if organization_id:
            validated_data['organization'] = Organization.objects.get(pk=organization_id)
        
        # Now safely update the rest
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class UsageAccountSerializer(GenericSerializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())

    class Meta:
        model = UsageAccount
        fields = '__all__'

    def create(self, validated_data):
        organization_id = validated_data.pop('organization_id')
        validated_data['organization'] = Organization.objects.get(pk=organization_id)
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        organization_id = validated_data.pop('organization_id', None)
        if organization_id:
            validated_data['organization'] = Organization.objects.get(pk=organization_id)
        
        # Now safely update the rest
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance    


class LynnbrookAccountSerializer(GenericSerializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=False, allow_null=True)

    class Meta:
        model = LynnbrookAccount
        fields = '__all__'

    def create(self, validated_data):
        organization_id = validated_data.pop('organization_id')
        validated_data['organization'] = Organization.objects.get(pk=organization_id)
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        organization_id = validated_data.pop('organization_id', None)
        if organization_id:
            validated_data['organization'] = Organization.objects.get(pk=organization_id)
        
        # Now safely update the rest
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance     
