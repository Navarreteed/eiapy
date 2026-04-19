"""Internal helpers: param normalisation and date validation."""

from __future__ import annotations

import re
from typing import Any

_VALID_FREQUENCIES = {"daily", "weekly", "monthly", "quarterly", "annual"}
_DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def validate_frequency(freq: str | None) -> str | None:
    """Return *freq* unchanged if valid, else raise ``ValueError``."""
    if freq is None:
        return None
    if freq not in _VALID_FREQUENCIES:
        raise ValueError(
            f"Invalid frequency {freq!r}. "
            f"Must be one of: {sorted(_VALID_FREQUENCIES)}."
        )
    return freq


def validate_date(value: str | None, name: str) -> str | None:
    """Validate a date string in ``YYYY``, ``YYYY-MM`` or ``YYYY-MM-DD`` form."""
    if value is None:
        return None
    if not _DATE_RE.match(value):
        raise ValueError(
            f"Invalid {name}={value!r}. Expected YYYY, YYYY-MM or YYYY-MM-DD."
        )
    return value


def as_list(value: str | list[str] | None) -> list[str] | None:
    """Coerce a string or list into a list (or ``None`` if value is None)."""
    if value is None:
        return None
    return [value] if isinstance(value, str) else list(value)


def build_params(
    *,
    data: list[str] | None = None,
    facets: dict[str, list[str]] | None = None,
    frequency: str | None = None,
    start: str | None = None,
    end: str | None = None,
    sort: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build a query-parameter dict for the EIA v2 API."""
    params: dict[str, Any] = {}
    if data:
        params["data[]"] = data
    if facets:
        for name, values in facets.items():
            if values:
                params[f"facets[{name}][]"] = values
    if frequency:
        params["frequency"] = frequency
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    if sort:
        for i, spec in enumerate(sort):
            if "column" in spec:
                params[f"sort[{i}][column]"] = spec["column"]
            if "direction" in spec:
                params[f"sort[{i}][direction]"] = spec["direction"]
    return params
