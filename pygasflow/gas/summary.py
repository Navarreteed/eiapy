"""Natural gas summary (``/natural-gas/sum/``) and metadata helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..client import EIAClient
from ..routes import resolve_route
from ..utils import build_params, validate_date, validate_frequency


def get_summary(
    *,
    route: str | None = None,
    frequency: str = "monthly",
    start: str | None = None,
    end: str | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch the EIA natural gas summary dataset.

    Pulls from the EIA endpoint ``/natural-gas/sum/lsum`` (linked
    summary) by default.

    Args:
        route: Sub-route variant. One of ``"lsum"`` (default), ``"snd"``,
            ``"sndm"``.
        frequency: ``"monthly"`` (default), ``"quarterly"`` or
            ``"annual"``.
        start: Start of date range, e.g. ``"2020-01"``.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame of summary rows.

    Example:
        >>> from pygasflow import get_summary
        >>> df = get_summary(frequency="annual", start="2010", end="2024")
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")

    params = build_params(frequency=frequency, start=start, end=end)
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("summary", route), params
    )


def get_available_series(
    endpoint: str, *, api_key: str | None = None
) -> dict[str, Any]:
    """List the facets and data columns queryable for an endpoint.

    Calls the EIA metadata endpoint (route without ``/data``) and
    returns the parsed payload — useful for discovering valid
    facet values, frequencies, and data columns.

    Args:
        endpoint: Friendly name (``"consumption"``, ``"prices"``,
            ``"storage"``, ``"production"``, ``"movements"``,
            ``"summary"``, ``"exploration"``) or a raw EIA route like
            ``"natural-gas/cons/pns"``.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        The parsed metadata dictionary, with keys such as
        ``frequency``, ``facets``, ``data`` and ``defaultFrequency``.

    Example:
        >>> from pygasflow import get_available_series
        >>> meta = get_available_series("consumption")
        >>> sorted(meta.get("facets", []))
    """
    from ..routes import ROUTE_REGISTRY

    # Check if it's a known group name — resolve to its default route
    if endpoint in ROUTE_REGISTRY:
        rg = ROUTE_REGISTRY[endpoint]
        route = rg.routes[rg.default]
    else:
        # Treat as a raw route string
        route = endpoint
    return EIAClient(api_key=api_key).fetch_metadata(route)
