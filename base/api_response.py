# utils/api_response.py
from rest_framework.response import Response
from typing import Any, Dict, List, Optional

class APIResponse:
    """
    Standardized API response format for all endpoints
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        pagination: Optional[Dict] = None
    ) -> Response:
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        
        if pagination:
            response["pagination"] = pagination
            
        return Response(response, status=status_code)
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        status_code: int = 400,
        errors: Optional[List[Dict]] = None
    ) -> Response:
        response = {
            "success": False,
            "message": message,
            "errors": errors or []
        }
        return Response(response, status=status_code)