from rest_framework import status
from base.api_response import APIResponse

def validate_artist_profile_management(artist, request):
    if artist.user != request.user and not request.user.is_staff:
        return APIResponse.error(
            message="You can only manage your own availability",
            status_code=status.HTTP_403_FORBIDDEN
        )