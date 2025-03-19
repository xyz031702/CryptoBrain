"""Basic exceptions for the SocialPulse module."""

class SocialPulseException(Exception):
    """Base exception for all SocialPulse module exceptions."""
    pass

class ConnectorException(SocialPulseException):
    """Base exception for connector-related errors."""
    pass

class AuthenticationException(ConnectorException):
    """Exception raised when authentication to an external service fails."""
    pass

class RateLimitException(ConnectorException):
    """Exception raised when a rate limit is hit for an external service."""
    
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after
