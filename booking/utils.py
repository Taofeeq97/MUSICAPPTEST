from rest_framework import status
from base.api_response import APIResponse

def validate_venue_owner(venue, request):
    if venue.owner != request.user and not request.user.is_staff:
        return APIResponse.error(
            message="You don't have permission to edit this venue",
            status_code=status.HTTP_403_FORBIDDEN
        )