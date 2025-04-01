from django.utils import timezone
from rest_framework import serializers

from artist.models import Artist, Review, ArtistPortfolioItem, ArtistAvailability
from authentication.serializers import UserProfileSerializer
from base.constants import MEDIATYPE


class ArtistSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Artist
        fields = [
            'id', 'user', 'user_details', 'stage_name', 'genre', 
            'hourly_rate', 'portfolio_url', 'instagram_handle',
            'spotify_profile', 'available_for_booking'
        ]
        read_only_fields = ['id', 'user_details']
    
    def get_user_details(self, obj):
        if obj.user:
            return UserProfileSerializer(obj.user).data
        return None
    
    def validate_hourly_rate(self, value):
        if value <= 0:
            raise serializers.ValidationError("Hourly rate must be positive.")
        return value
    
    def validate_instagram_handle(self, value):
        if value and not value.startswith('@'):
            raise serializers.ValidationError("Instagram handle must start with @")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_details = serializers.SerializerMethodField()
    artist_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'reviewer_details', 'artist', 'artist_details',
            'booking', 'rating', 'comment'
        ]
        read_only_fields = ['id', 'reviewer_details', 'artist_details']
    
    def get_reviewer_details(self, obj):
        if obj.reviewer:
            return UserProfileSerializer(obj.reviewer).data
        return None
    
    def get_artist_details(self, obj):
        if obj.artist:
            return ArtistSerializer(obj.artist).data
        return None
    
    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate(self, data):
        if data['artist'].user == data['reviewer']:
            raise serializers.ValidationError("Artists cannot review themselves.")
        return data
    

class ArtistPortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistPortfolioItem
        fields = [
            'id', 'artist', 'title', 'description',
            'media_url', 'media_type'
        ]
        read_only_fields = ['id']
    
    def validate_media_type(self, value):
        
        if value not in MEDIATYPE.choices:
            raise serializers.ValidationError(
                f"Invalid media type. Must be one of: {MEDIATYPE.choices}"
            )
        return value
    
    def validate_media_url(self, value):
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Media URL must be a valid URL")
        return value


class ArtistAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistAvailability
        fields = [
            'id', 'artist', 'date', 'start_time',
            'end_time', 'is_available'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time.")
        
        if data['date'] < timezone.now().date():
            raise serializers.ValidationError("Cannot set availability for past dates.")
        
        qs = ArtistAvailability.objects.filter(
                artist=data['artist'],
                date=data['date'],
                start_time__lt=data['end_time'],
                end_time__gt=data['start_time'],
            )
        
        if self.instance:
            qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("This time slot overlaps with existing availability.")
        
        return data