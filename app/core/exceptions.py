"""Custom exceptions for the application."""
from typing import Any, Optional


class MovieReservationException(Exception):
    """Base exception for the application."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(MovieReservationException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(message, status_code=404, details=details)


class UnauthorizedException(MovieReservationException):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str = "Unauthorized", details: Optional[Any] = None):
        super().__init__(message, status_code=401, details=details)


class ForbiddenException(MovieReservationException):
    """Exception raised when access is forbidden."""
    
    def __init__(self, message: str = "Forbidden", details: Optional[Any] = None):
        super().__init__(message, status_code=403, details=details)


class BadRequestException(MovieReservationException):
    """Exception raised for bad requests."""
    
    def __init__(self, message: str = "Bad request", details: Optional[Any] = None):
        super().__init__(message, status_code=400, details=details)


class ConflictException(MovieReservationException):
    """Exception raised for resource conflicts."""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None):
        super().__init__(message, status_code=409, details=details)


class ValidationException(MovieReservationException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str = "Validation error", details: Optional[Any] = None):
        super().__init__(message, status_code=422, details=details)
