"""eiapy — Python client for the U.S. EIA Open Data API v2."""

from .exceptions import (
    AuthenticationError,
    EIAError,
    MissingAPIKeyError,
    NotFoundError,
    RateLimitError,
    RequestFailedError,
)
from .query import get_data, get_metadata
from .routes import REGISTRY, list_routes, resolve_route

# Natural gas convenience functions
from .categories import (
    get_available_series,
    get_consumption,
    get_exploration,
    get_movements,
    get_prices,
    get_production,
    get_storage,
    get_summary,
)

__version__ = "0.2.0"


def list_categories() -> list[str]:
    """Return all known EIA API categories."""
    return REGISTRY.list_categories()


def list_groups(category: str) -> dict[str, list[str]]:
    """Return ``{group: [variants]}`` for a category."""
    return REGISTRY.list_groups(category)


__all__ = [
    # Generic query
    "get_data",
    "get_metadata",
    # Discovery
    "list_categories",
    "list_groups",
    "list_routes",
    "resolve_route",
    # Natural gas convenience
    "get_consumption",
    "get_exploration",
    "get_movements",
    "get_prices",
    "get_production",
    "get_storage",
    "get_summary",
    "get_available_series",
    # Exceptions
    "EIAError",
    "MissingAPIKeyError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "RequestFailedError",
]
