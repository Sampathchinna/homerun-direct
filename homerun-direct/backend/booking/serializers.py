from core.serializers import GenericSerializer
from .models import BookingNetDetails
class BookingNetDetailsSerializer(GenericSerializer):
    class Meta:
        model = BookingNetDetails
        fields = '__all__'
        ref_name = 'booking_booking_net_details'

from .models import Bookings
class BookingsSerializer(GenericSerializer):
    class Meta:
        model = Bookings
        fields = '__all__'
        ref_name = 'booking_bookings'

from .models import BookingsFees
class BookingsFeesSerializer(GenericSerializer):
    class Meta:
        model = BookingsFees
        fields = '__all__'
        ref_name = 'booking_bookings_fees'

from .models import LineItems
class LineItemsSerializer(GenericSerializer):
    class Meta:
        model = LineItems
        fields = '__all__'
        ref_name = 'booking_line_items'
