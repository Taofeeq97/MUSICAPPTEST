from django.urls import path
from booking.views import (
    VenueListView,
    VenueDetailView,
    EventListView,
    EventDetailView,
    BookingListView,
    BookingDetailView,
    PaymentView,
    VerifyPaymentView
)

urlpatterns = [
    path('', BookingListView.as_view(), name='booking-list'),
    path('<uuid:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('venues/', VenueListView.as_view(), name='venue-list'),
    path('venues/<int:pk>/', VenueDetailView.as_view(), name='venue-detail'),
    path('events/', EventListView.as_view(), name='event-list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('payments/', PaymentView.as_view(), name='payment-create'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
]