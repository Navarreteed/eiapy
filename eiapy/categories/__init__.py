"""Category-specific convenience functions."""

from .natural_gas import (
    get_available_series,
    get_consumption,
    get_exploration,
    get_movements,
    get_prices,
    get_production,
    get_storage,
    get_summary,
)

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
