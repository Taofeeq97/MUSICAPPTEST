from django.urls import path
from artist.views import (
    ArtistListView,
    ArtistDetailView,
    ReviewListView,
    ArtistPortfolioListView,
    ArtistAvailabilityView,
    ArtistAvailabilityDetailView
)

urlpatterns = [
    path('', ArtistListView.as_view(), name='artist-list'),
    path('<int:pk>/', ArtistDetailView.as_view(), name='artist-detail'),
    path('reviews/', ReviewListView.as_view(), name='review-list'),
    path('portfolio/', ArtistPortfolioListView.as_view(), name='portfolio-list'),
    path('availability/', ArtistAvailabilityView.as_view(), name='availability-list'),
    path('availability/<uuid:pk>/', ArtistAvailabilityDetailView.as_view(), name='availability-detail'),
]