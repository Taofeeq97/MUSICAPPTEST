import uuid
from django.db import models
from authentication.models import User
from base.constants import BookingStatus, EventStatus, PaymentStatus
from base.models import BaseModel


# Create your models here.
class Venue(BaseModel):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True, related_name='venues')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()
    description = models.TextField()
    amenities = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class Event(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL,null=True, blank=True, related_name='events')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=EventStatus.choices, default=EventStatus.PUBLISHED)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_slots = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    

class Booking(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    artist = models.ForeignKey('artist.Artist', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    booker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    special_requests = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"


class Payment(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL,null=True, blank=True, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    paid_at = models.DateTimeField(blank=True, null=True)
    reference_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.reference_number}"