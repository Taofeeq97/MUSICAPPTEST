from django.db.models import TextChoices


class UserType(TextChoices):
    ARTIST='ARTIST'
    VENUE_OWNER='VENUE_OWNER'
    CLIENT='CLIENT'


class EventStatus(TextChoices):
    DRAFT='DRAFT'
    PUBLISHED='PUBLISHED'
    CANCELLED='CANCELLED'
    COMPLETED='COMPLETED'


class BookingStatus(TextChoices):
    PENDING='PENDING'
    CONFIRMED='CONFIRMED'
    CANCELLED='CANCELLED'
    COMPLETED='COMPLETED'


class PaymentStatus(TextChoices):
    PENDING='PENDING'
    COMPLETED='COMPLETED'
    FAILED='FAILED'
    REFUNDED='REFUNDED'


class MEDIATYPE(TextChoices):
    IMAGE='IMAGE'
    VIDEO='VIDEO'
    AUDIO='AUDIO'
