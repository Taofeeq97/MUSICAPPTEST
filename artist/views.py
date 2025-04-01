from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone 
from rest_framework import filters
from rest_framework import generics, permissions, status
from artist.models import Artist, Review, ArtistPortfolioItem, ArtistAvailability
from artist.serializers import (
    ArtistSerializer,
    ReviewSerializer,
    ArtistPortfolioItemSerializer,
    ArtistAvailabilitySerializer
)
from artist.utils import validate_artist_profile_management
from base.api_response import APIResponse
from base.utils import CustomPagination


class ArtistListView(generics.ListCreateAPIView):
    queryset = Artist.active_objects.select_related('user')
    serializer_class = ArtistSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'genre': ['exact', 'icontains'],
        'hourly_rate': ['gte', 'lte', 'exact'],
        'available_for_booking': ['exact'],
        'user__is_active': ['exact'], 
    }
    search_fields = [
        'stage_name', 
        'genre',
        'user__email',
        'user__first_name', 
        'user__last_name'
    ]
    ordering_fields = [
        'stage_name', 
        'hourly_rate', 
        'created_at', 
        'user__date_joined'
    ]
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if Artist.active_objects.filter(user=request.user).exists():
                return APIResponse.error(
                    message="User already has an artist profile",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save(user=request.user)
            return APIResponse.success(
                data=serializer.data,
                message="Artist profile created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return APIResponse.error(
            message="Artist creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class ArtistDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Artist.active_objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        validate_artist_profile_management(instance, request)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="Artist updated successfully"
            )
        return APIResponse.error(
            message="Update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        validate_artist_profile_management(instance, request)
        instance.delete()
        return APIResponse.success(message="Artist deleted successfully")


class ReviewListView(generics.ListCreateAPIView):
    queryset = Review.active_objects.select_related('reviewer', 'artist', 'booking')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'artist': ['exact'],
        'rating': ['exact', 'gte', 'lte'],
        'created_at': ['gte', 'lte', 'date'],
    }
    search_fields = [
        'comment',
        'artist__stage_name',
        'reviewer__email',
        'reviewer__first_name',
        'reviewer__last_name'
    ]
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if Review.active_objects.filter(
                reviewer=request.user,
                booking = serializer.validated_data['booking'],
                artist=serializer.validated_data['artist']
            ).exists():
                return APIResponse.error(
                    message="You have already reviewed this artist",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save(reviewer=request.user)
            return APIResponse.success(
                data=serializer.data,
                message="Review created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return APIResponse.error(
            message="Review creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    

class ArtistPortfolioListView(generics.ListCreateAPIView):
    queryset = ArtistPortfolioItem.active_objects.all()
    serializer_class = ArtistPortfolioItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            artist = serializer.validated_data['artist']
            if artist.user != request.user and not request.user.is_staff:
                return APIResponse.error(
                    message="You can only add to your own portfolio",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="Portfolio item added successfully",
                status_code=status.HTTP_201_CREATED
            )
        return APIResponse.error(
            message="Portfolio item creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    

class ArtistAvailabilityView(generics.ListCreateAPIView):
    queryset = ArtistAvailability.active_objects.all()
    serializer_class = ArtistAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(date__gte=timezone.now().date()))
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            artist = serializer.validated_data['artist']
            validate_artist_profile_management(artist, request)
            serializer.save()

            return APIResponse.success(
                data=serializer.data,
                message="Availability set successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return APIResponse.error(
            message="Availability creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )



class ArtistAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ArtistAvailability.active_objects.all()
    serializer_class = ArtistAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        validate_artist_profile_management(instance.artist, request)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="Availability updated successfully"
            )
        
        return APIResponse.error(
            message="Update failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        validate_artist_profile_management(instance.artist, request)
        instance.delete()
        return APIResponse.success(message="Availability removed successfully")