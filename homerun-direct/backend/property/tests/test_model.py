from django.test import TestCase
from django.core.exceptions import ValidationError
from property.models import *
from datetime import date


class SetupBase(TestCase):
    """Base class to create shared Property & Organization."""
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org")
        self.prop = Property.objects.create(name="Test Property", organization=self.org)


class GuestControlsModelTest(SetupBase):
    
    def make_valid_guest_controls(self, **overrides):
        """Helper to create GuestControls with valid defaults."""
        data = {
            "property": self.prop,
            "children": {"allowed": True},
            "smoking": {"allowed": False}
        }
        data.update(overrides)
        return GuestControls(**data)

    def test_valid_guest_controls_passes(self):
        """Ensure valid GuestControls instance passes validation."""
        gc = self.make_valid_guest_controls()
        try:
            gc.full_clean()
        except ValidationError:
            self.fail("Valid GuestControls raised ValidationError unexpectedly.")

    def test_children_must_be_dict(self):
        """Test that non-dict children field raises ValidationError."""
        gc = self.make_valid_guest_controls(children="not-a-dict")
        with self.assertRaises(ValidationError):
            gc.full_clean()


class UnitsModelTest(SetupBase):
    def test_negative_values_raise_validation_error(self):
        bad_data = {
            "num_sleep_in_beds": -1,
            "num_bedrooms": -2,
            "num_bathrooms": -1,
            "num_lounge": -1,
            "num_parking_space": -1
        }
        for field, value in bad_data.items():
            unit_data = {
                "property": self.prop,
                field: value
            }
            unit = Units(**unit_data)
            with self.assertRaises(ValidationError, msg=f"{field} failed"):
                unit.full_clean()


class BedroomsBathroomsModelTest(SetupBase):
    def setUp(self):
        super().setUp()
        self.unit = Units.objects.create(property=self.prop)

    def test_negative_room_counts_raise_error(self):
        bad_data = {
            "num_of_bedrooms": -1,
            "num_of_bathrooms": -1,
            "num_of_livingrooms": -1,
            "num_sleep_in_beds": -1
        }
        for field, value in bad_data.items():
            bb_data = {
                "unit": self.unit,
                field: value
            }
            bb = BedroomsBathrooms(**bb_data)
            with self.assertRaises(ValidationError, msg=f"{field} failed"):
                bb.full_clean()

class ReservationNewModelTest(TestCase):
    
    def make_valid_reservation(self, **overrides):
        """Helper to create a ReservationNew with required fields only."""
        data = {
            "booking_range": {},
            "booking_type": "online",
            "check_in": date(2025, 5, 20),
            "check_out": date(2025, 5, 22),
            "customer_email": "test@example.com",
            "customer_name": "John Doe",
            "customer_telephone": "1234567890",
            "listing_id": 1,
            "total": 100.00
        }
        data.update(overrides)
        return ReservationNew(**data)

    def test_valid_reservation_passes(self):
        """Test that a valid reservation passes validation."""
        res = self.make_valid_reservation()
        try:
            res.full_clean()  # Should not raise
        except ValidationError:
            self.fail("Valid reservation raised ValidationError unexpectedly.")

    def test_check_out_before_check_in_raises_error(self):
        """Test that check-out before check-in raises ValidationError."""
        res = self.make_valid_reservation(
            check_in=date(2025, 5, 20),
            check_out=date(2025, 5, 19)
        )
        with self.assertRaises(ValidationError):
            res.full_clean()

    def test_check_out_equal_to_check_in_raises_error(self):
        """Test that check-out equal to check-in also raises ValidationError."""
        res = self.make_valid_reservation(
            check_in=date(2025, 5, 20),
            check_out=date(2025, 5, 20)
        )
        with self.assertRaises(ValidationError):
            res.full_clean()


class PricingModelTest(SetupBase):
    def setUp(self):
        super().setUp()
        self.unit = Units.objects.create(property=self.prop)
        self.vehicle = Vehicle.objects.create(name="Test Vehicle") 

    def make_valid_pricing(self, **overrides):
        data = {
            "unit": self.unit,
            "organization": self.org,
            "default_nightly_weekday": 100.00,
            "default_nightly_weekend": 120.00,
            "discount_full_week": 10.0,
            "discount_full_month": 15.0,
            "pricing_calendar": {},
            "additional_guest_amount_cents": 500,
            "additional_guest_start": 2,
            "vehicle": self.vehicle,
        }
        data.update(overrides)
        return Pricing(**data)

    def test_valid_pricing_passes(self):
        pricing = self.make_valid_pricing()
        try:
            pricing.full_clean()
        except ValidationError:
            self.fail("Valid Pricing raised ValidationError unexpectedly.")

    def test_negative_weekday_rate_raises_error(self):
        pricing = self.make_valid_pricing(default_nightly_weekday=-10)
        with self.assertRaises(ValidationError):
            pricing.full_clean()

    def test_negative_weekend_rate_raises_error(self):
        pricing = self.make_valid_pricing(default_nightly_weekend=-5)
        with self.assertRaises(ValidationError):
            pricing.full_clean()

    def test_weekly_discount_below_zero_raises_error(self):
        pricing = self.make_valid_pricing(discount_full_week=-1)
        with self.assertRaises(ValidationError):
            pricing.full_clean()

    def test_weekly_discount_above_100_raises_error(self):
        pricing = self.make_valid_pricing(discount_full_week=101)
        with self.assertRaises(ValidationError):
            pricing.full_clean()

    def test_monthly_discount_below_zero_raises_error(self):
        pricing = self.make_valid_pricing(discount_full_month=-5)
        with self.assertRaises(ValidationError):
            pricing.full_clean()

    def test_monthly_discount_above_100_raises_error(self):
        pricing = self.make_valid_pricing(discount_full_month=150)
        with self.assertRaises(ValidationError):
            pricing.full_clean()