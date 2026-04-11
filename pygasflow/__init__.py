"""pygasflow — clean Python access to EIA natural gas data."""

from .exceptions import (
    AuthenticationError,
    EIAError,
    MissingAPIKeyError,
    NotFoundError,
    RateLimitError,
    RequestFailedError,
)
from .gas import (
    get_available_series,
    get_consumption,
    get_exploration,
    get_movements,
    get_prices,
    get_production,
    get_storage,
    get_summary,
)
from .routes import list_routes, resolve_route

__version__ = "0.1.1"

__all__ = [
    # Data functions
    "get_consumption",
    "get_exploration",
    "get_movements",
    "get_prices",
    "get_production",
    "get_storage",
    "get_summary",
    "get_available_series",
    # Route helpers
    "list_routes",
    "resolve_route",
    # Exceptions
    "EIAError",
    "MissingAPIKeyError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "RequestFailedError",
]
