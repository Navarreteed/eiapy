"""Exceptions raised by eiapy."""


class EIAError(Exception):
    """Base exception for all eiapy errors."""


class MissingAPIKeyError(EIAError):
    """Raised when no API key is provided and EIA_API_KEY is not set."""


class AuthenticationError(EIAError):
    """Raised when the EIA API rejects the API key (HTTP 401/403)."""


class RateLimitError(EIAError):
    """Raised when the EIA API returns HTTP 429."""


class NotFoundError(EIAError):
    """Raised when the requested route does not exist (HTTP 404)."""


class RequestFailedError(EIAError):
    """Raised when the EIA API returns any other error response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
