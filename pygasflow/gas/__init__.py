"""Natural gas data endpoints."""

from .consumption import get_consumption
from .exploration import get_exploration
from .movements import get_movements
from .prices import get_prices
from .production import get_production
from .storage import get_storage
from .summary import get_available_series, get_summary

__all__ = [
    "get_consumption",
    "get_exploration",
    "get_movements",
    "get_prices",
    "get_production",
    "get_storage",
    "get_summary",
    "get_available_series",
]
