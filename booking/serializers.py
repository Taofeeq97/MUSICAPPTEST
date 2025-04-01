from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers

from artist.serializers import ArtistSerializer
from authentication.serializers import UserProfileSerializer
from base.constants import EventStatus, BookingStatus
from booking.models import Venue, Event, Booking, Payment


class VenueSerializer(serializers.ModelSerializer):
    owner_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'owner', 'owner_details', 'address', 'city', 
            'state', 'zip_code', 'capacity', 'description', 'amenities'
        ]
        read_only_fields = ['id', 'owner_details']
    
    def get_owner_details(self, obj):
        if obj.owner:
            return UserProfileSerializer(obj.owner).data
        return None
    
    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Capacity must be positive.")
        return value

class EventSerializer(serializers.ModelSerializer):
    venue_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'venue', 'venue_details',
            'start_time', 'end_time', 'status', 'ticket_price',
            'available_slots'
        ]
        read_only_fields = [
            'id', 'venue_details'
        ]
    
    def get_venue_details(self, obj):
        if obj.venue:
            return VenueSerializer(obj.venue).data
        return None
    
    def get_available_slots(self, obj):
        confirmed_bookings = obj.bookings.filter(status='CONFIRMED').count()
        return max(0, obj.available_slots - confirmed_bookings)
    
    def validate(self, data):
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    "End time must be after start time."
                )
            
            if data['start_time'] < timezone.now() + timedelta(hours=1):
                print(data['start_time'])
                print(timezone.now())
                raise serializers.ValidationError(
                    "Events must be scheduled at least 1 hour in advance."
                )
        
        if 'ticket_price' in data and data['ticket_price'] <= 0:
            raise serializers.ValidationError(
                "Ticket price must be positive."
            )
        
        return data

class BookingSerializer(serializers.ModelSerializer):
    event_details = serializers.SerializerMethodField()
    artist_details = serializers.SerializerMethodField()
    booker_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'event', 'event_details', 'artist', 'artist_details',
            'booker', 'booker_details', 'status', 'amount',
            'special_requests', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 
            'event_details', 'artist_details', 'booker_details'
        ]
    
    def get_event_details(self, obj):
        if obj.event:
            return EventSerializer(obj.event).data
        return None
    
    def get_artist_details(self, obj):
        if obj.artist:
            return ArtistSerializer(obj.artist).data
        return None
    
    def get_booker_details(self, obj):
        if obj.booker:
            return UserProfileSerializer(obj.booker).data
        return None
    
    def validate(self, data):
        request = self.context.get('request')
        if 'amount' in data and data['amount'] <= 0:
            raise serializers.ValidationError(
                {"amount": "Booking amount must be positive."}
            )
        
        if 'event' in data:
            event = data['event']
            
            if event.status != EventStatus.PUBLISHED:
                raise serializers.ValidationError(
                    {"event": "Cannot book an unpublished or cancelled event."}
                )
            
            if event.start_time < timezone.now():
                raise serializers.ValidationError(
                    {"event": "Cannot book a past event."}
                )
            
            if request and hasattr(request, 'user'):
                if event.venue.owner != request.user:
                    raise serializers.ValidationError(
                        {"event": "Only the event organizer can book artists for this event."}
                    )
        
        if 'artist' in data and data['artist']:
            artist = data['artist']
            if not artist.available_for_booking:
                raise serializers.ValidationError(
                    {"artist": "Artist is not available for bookings."}
                )
        
            if 'event' in data and data['event']:
                event = data['event']
                duration_hours = (event.end_time - event.start_time).total_seconds() / 3600
                expected_amount = round(float(artist.hourly_rate) * duration_hours, 2)
                if 'amount' in data and abs(float(data['amount']) - expected_amount) > 0.01:
                    raise serializers.ValidationError(
                        {"amount": f"Amount should be {expected_amount} based on artist's hourly rate and event duration."}
                    )
                conflicting_bookings = Booking.active_objects.filter(
                    artist=artist,
                    event__start_time__lt=event.end_time,
                    event__end_time__gt=event.start_time,
                    status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
                ).exclude(id=self.instance.id if self.instance else None)
                
                if conflicting_bookings.exists():
                    raise serializers.ValidationError(
                        {"artist": "Artist is already booked for this time slot."}
                    )
        
        return data
    
    def create(self, validated_data):
        if 'amount' not in validated_data and 'artist' in validated_data and 'event' in validated_data:
            artist = validated_data['artist']
            event = validated_data['event']
            duration_hours = (event.end_time - event.start_time).total_seconds() / 3600
            validated_data['amount'] = round(float(artist.hourly_rate) * duration_hours, 2)
        
        return super().create(validated_data)
    


class PaymentSerializer(serializers.ModelSerializer):
    booking_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'booking_details', 'amount',
            'payment_method', 'transaction_id', 'status',
            'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'booking_details', 'paid_at'
        ]
    
    def get_booking_details(self, obj):
        if obj.booking:
            return BookingSerializer(obj.booking).data
        return None
    
    def validate(self, data):
        if 'amount' in data and 'booking' in data:
            if data['amount'] != data['booking'].amount:
                raise serializers.ValidationError(
                    "Payment amount must match booking amount."
                )
        if not data.get('booking'):
            raise serializers.ValidationError(
                "Booking not selected"
            )
            

        if data['booking'].status != BookingStatus.PENDING:
            raise serializers.ValidationError(
                "Payment can only be made for pending bookings."
            )
        
        return data
    

class VerifyPaymentSerializer(serializers.Serializer):
    reference_number = serializers.CharField(max_length=100)
    
    def validate_reference_number(self, value):
        """Validate that payment exists with this reference"""
        if not Payment.active_objects.filter(reference_number=value).exists():
            raise serializers.ValidationError("Payment with this reference does not exist")
        return value