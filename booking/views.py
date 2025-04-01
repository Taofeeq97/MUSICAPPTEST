from django.conf import settings
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters, status
from rest_framework import filters
from base.api_response import APIResponse
from base.constants import BookingStatus, EventStatus, PaymentStatus
from base.utils import MonnifyClient, CustomPagination
from booking.models import Venue, Event, Booking, Payment
from booking.serializers import (
    VenueSerializer,
    EventSerializer,
    BookingSerializer,
    PaymentSerializer,
    VerifyPaymentSerializer
)
from booking.utils import validate_venue_owner


monnify = MonnifyClient()

class VenueListView(generics.ListCreateAPIView):
    queryset = Venue.active_objects.select_related('owner').all()
    serializer_class = VenueSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'capacity': ['gte', 'lte', 'exact'],
        'city': ['exact', 'icontains'],
        'state': ['exact', 'icontains'],
        'owner__is_active': ['exact'], 
    }
    search_fields = [
        'name',
        'address',
        'city',
        'state',
        'amenities',
        'owner__email',
        'owner__first_name',
        'owner__last_name'
    ]
    ordering_fields = ['name', 'capacity', 'created_at']
    ordering = ['-created_at'] 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return APIResponse.success(
                data=serializer.data,
                message="Venue created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return APIResponse.error(
            message="Venue creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class VenueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Venue.active_objects.all()
    serializer_class = VenueSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        validate_venue_owner(instance, request)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="Venue updated successfully"
            )
        return APIResponse.error(
            message="Update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    def destroy(self, request, *args, **kwargs):
        object = self.get_object()
        object.delete()
        return APIResponse.success(
                data=None,
                message="Venue deleted successfully"
            )


class EventListView(generics.ListCreateAPIView):
    queryset = Event.active_objects.filter(
        status=EventStatus.PUBLISHED,
        start_time__gte=timezone.now()
    ).select_related('venue')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'venue': ['exact'],
        'ticket_price': ['gte', 'lte', 'exact'],
        'start_time': ['gte', 'lte', 'date'],
        'available_slots': ['gte', 'lte'],
    }
    search_fields = [
        'title',
        'description',
        'venue__name',
        'venue__city'
    ]
    ordering_fields = ['start_time', 'ticket_price', 'available_slots']
    ordering = ['start_time']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            venue = serializer.validated_data.get('venue')
            if venue and venue.owner != request.user and not request.user.is_staff:
                return APIResponse.error(
                    message="You can only create events for your own venues",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="Event created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return APIResponse.error(
            message="Event creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.active_objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.venue.owner != request.user and not request.user.is_staff:
            return APIResponse.error(
                message="You don't have permission to edit this event",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="Event updated successfully"
            )
        return APIResponse.error(
            message="Update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    def destroy(self, request, *args, **kwargs):
        object = self.get_object()
        if object.bookings.filter(status__in=[
            BookingStatus.PENDING, BookingStatus.CONFIRMED, 
            BookingStatus.CONFIRMED]).exist():
            return APIResponse.error(
                message="Cannot delete Event with completed or pending booking"
            )
        object.delete()
        return APIResponse.success(
            message="Data deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )
    

class BookingListView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'event': ['exact'],
        'artist': ['exact'],
        'status': ['exact'],
        'created_at': ['date', 'gte', 'lte'],
    }
    search_fields = [
        'event__title',
        'artist__stage_name',
        'special_requests',
        'booker__email',
        'booker__first_name',
        'booker__last_name'
    ]
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Booking.active_objects.select_related(
            'event', 'artist', 'booker'
        )
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(booker=self.request.user)
            
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            event = serializer.validated_data.get('event')
            if event and event.venue.owner != request.user:
                return APIResponse.error(
                    message="You can only book artists for your own events.",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            serializer.save(booker=request.user)
            return APIResponse.success(
                data=serializer.data,
                message="Booking created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return APIResponse.error(
            message="Booking creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.active_objects.select_related('event', 'artist', 'booker').all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.active_objects.select_related('event', 'artist', 'booker').all()
        return Booking.active_objects.filter(booker=self.request.user).select_related('event', 'artist', 'booker').all()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != BookingStatus.PENDING and not request.user.is_staff:
            return APIResponse.error(
                message="Only pending bookings can be modified",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="Booking updated successfully"
            )
        return APIResponse.error(
            message="Update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            return APIResponse.error(
                message="Only pending or confirmed bookings can be cancelled",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        instance.status = BookingStatus.CANCELLED
        instance.delete()
        return APIResponse.success(
            data=BookingSerializer(instance).data,
            message="Booking cancelled successfully"
        )
    

class PaymentView(generics.CreateAPIView):
    queryset = Payment.active_objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.validated_data['booking']
            
            if booking.booker != request.user and not request.user.is_staff:
                return APIResponse.error(
                    message="You can only pay for your own bookings",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            if Payment.active_objects.filter(booking=booking).exists():
                return APIResponse.error(
                    message="Payment already exists for this booking",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                monnify = MonnifyClient()
                payment_data = monnify.generate_checkout_url(booking, request.user)
                payment = Payment.active_objects.create(
                    booking=booking,
                    amount=booking.amount,
                    payment_method="ONLINE",
                    status=PaymentStatus.PENDING,
                    reference_number=payment_data['transaction_reference']
                )
                
                return APIResponse.success(
                    data={
                        'checkout_url': payment_data['checkout_url'],
                        'payment_id': str(payment.id),
                        'reference_number': payment.reference_number
                    },
                    message="Payment initialized successfully",
                    status_code=status.HTTP_201_CREATED
                )
                
            except Exception as e:
                return APIResponse.error(
                    message=str(e),
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
        return APIResponse.error(
            message="Payment processing failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    

class VerifyPaymentView(generics.GenericAPIView):
    serializer_class = VerifyPaymentSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference_number = serializer.validated_data['reference_number']
        
        try:
            payment = Payment.active_objects.get(reference_number=reference_number)
        except Payment.DoesNotExist:
            return APIResponse.error(
                message="Payment not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            monnify = MonnifyClient()
            verification = monnify.confirm_payment(reference_number)
            if not verification.get('success', False):
                return APIResponse.error(
                    message="Payment verification failed",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            transaction_data = verification['transaction']
            if transaction_data['status'] == 'PAID' and payment.status != PaymentStatus.COMPLETED:
                payment.status = PaymentStatus.COMPLETED
                payment.paid_at = timezone.datetime.strptime(
                    transaction_data['paid_on'],
                    '%Y-%m-%d %H:%M:%S.%f'
                ).replace(tzinfo=timezone.utc)
                payment.transaction_id = reference_number
                payment.save()
                
                if payment.booking:
                    payment.booking.status = BookingStatus.CONFIRMED
                    payment.booking.save()
            
            data = {
                'payment_status': transaction_data['status'],
                'amount_paid': transaction_data['amount_paid'],
                'paid_at': transaction_data['paid_on'],
                'transaction_reference': transaction_data['transaction_reference']
            }
            
            return APIResponse.success(
                message="Payment verified successfully",
                data=data
            )
            
        except Exception as e:
            return APIResponse.error(
                message=f"Error verifying payment: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )