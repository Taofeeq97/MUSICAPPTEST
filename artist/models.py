from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from authentication.models import User
from base.constants import MEDIATYPE
from base.models import BaseModel
from booking.models import Booking



class Artist(BaseModel):
    user = models.OneToOneField(User, on_delete=models.SET_NULL,null=True, blank=True, related_name='artist')
    stage_name = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    portfolio_url = models.URLField(blank=True, null=True)
    instagram_handle = models.CharField(max_length=50, blank=True, null=True)
    spotify_profile = models.URLField(blank=True, null=True)
    available_for_booking = models.BooleanField(default=True)

    def __str__(self):
        return self.stage_name
    

class Review(BaseModel):
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True, related_name='reviews_given')
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL,null=True, blank=True, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL,null=True, blank=True, related_name='review')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.artist.stage_name}"
    

class ArtistPortfolioItem(BaseModel):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    media_url = models.URLField()
    media_type = models.CharField(max_length=20, choices=MEDIATYPE.choices, default=MEDIATYPE.IMAGE)

    def __str__(self):
        return f"{self.title} - {self.artist.stage_name}"
    

class ArtistAvailability(BaseModel):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('artist', 'date', 'start_time', 'end_time')
        
    def __str__(self):
        return f"{self.artist.stage_name} - {self.date} {self.start_time}-{self.end_time}"