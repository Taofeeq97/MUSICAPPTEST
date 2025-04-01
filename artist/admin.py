from django.contrib import admin
from artist.models import Artist, ArtistAvailability, ArtistPortfolioItem

# Register your models here.

admin.site.register(Artist)
admin.site.register(ArtistAvailability)
admin.site.register(ArtistPortfolioItem)