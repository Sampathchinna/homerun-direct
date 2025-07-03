from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .viewsets import *

router = DefaultRouter()

# Register all the viewsets with the router
router.register(r'api/property', PropertyViewSet, basename='property')
router.register(r'api/images_property', ImagesPropertyViewSet, basename='images_property')
router.register(r'api/property_location', PropertyLocationViewSet, basename='property_location')
router.register(r'api/guest_controls', GuestControlsViewSet, basename='guest_controls')

# Property-related services
router.register(r'api/internet_options', InternetOptionsViewSet, basename='internet_options')
router.register(r'api/bedrooms_bathrooms', BedroomsBathroomsViewSet, basename='bedrooms_bathrooms')
router.register(r'api/bedrooms', BedroomsViewSet, basename='bedrooms')
router.register(r'api/living_rooms', LivingRoomsViewSet, basename='living_rooms')
router.register(r'api/bathroom', BathroomViewSet, basename='bathroom')
router.register(r'api/availability', AvailabilityViewSet, basename='availability')
router.register(r'api/pricing', PricingViewSet, basename='pricing')
router.register(r'api/deposits', DepositsViewSet, basename='deposits')
router.register(r'api/fee_accounts', FeeAccountsViewSet, basename='fee_accounts')
router.register(r'api/debit_account', DebitAccountViewSet, basename='debit_account')
router.register(r'api/credit_account', CreditAccountViewSet, basename='credit_account')
router.register(r'api/refund_policies', RefundPoliciesViewSet, basename='refund_policies')
router.register(r'api/units', UnitsViewSet, basename='units')
router.register(r'api/reservations', ReservationViewSet, basename='reservation')
router.register(r'api/reservations-information', ReservationInformationViewSet, basename='reservation-information')
router.register(r'api/line-items-fee', FeeLineItemViewSet, basename='fee-line-item')
router.register(r'api/line-items-tax', TaxLineItemViewSet, basename='tax-line-item')
router.register(r'api/property-listing', PropertyListingViewSet, basename='property-listing')
router.register(r'api/unit-listing', UnitListingViewSet, basename='unit-listing')
router.register(r'api/customer-information', CustomerInformationViewSet, basename='customer-information')
router.register(r'api/charges', ChargeViewSet, basename='charge')
router.register(r'api/payment-method', PaymentMethodViewSet, basename='payment-method')
router.register(r'api/notes', NoteViewSet, basename='note')
router.register(r'api/work-order', WorkOrderViewSet, basename='work-order')
router.register(r'api/work-report', WorkReportViewSet, basename='work-report')
router.register(r'api/deduction-account', DeductionAccountsViewSet, basename='deduction-account')
router.register(r'api/tax-account', TaxAccountsViewSet, basename='tax-account')
router.register(r'api/inventory-items', InventoryItemViewSet, basename='inventory-items')
router.register(r'api/usage-account', UsageAccountViewSet, basename='usage-account')


urlpatterns = [
    path("", include(router.urls)),
]
