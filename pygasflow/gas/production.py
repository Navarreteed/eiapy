"""Natural gas production (``/natural-gas/prod/``)."""

from __future__ import annotations

import pandas as pd

from ..client import EIAClient
from ..routes import resolve_route
from ..utils import as_list, build_params, validate_date, validate_frequency


def get_production(
    state: str | list[str] | None = None,
    *,
    route: str | None = None,
    frequency: str = "monthly",
    start: str | None = None,
    end: str | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch natural gas production volumes.

    Pulls from the EIA endpoint ``/natural-gas/prod/sum``.

    Args:
        state: U.S. state abbreviation (e.g. ``"TX"``) or list of
            abbreviations. ``None`` returns all areas (including
            U.S. totals).
        frequency: ``"monthly"`` (default), ``"quarterly"`` or
            ``"annual"``.
        start: Start of date range, e.g. ``"2020-01"``.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame of production rows. Columns include ``period``,
        ``duoarea``, ``process``, ``series``, ``value`` (million
        cubic feet) and ``units``.

    Example:
        >>> from pygasflow import get_production
        >>> df = get_production(state="TX", start="2020-01", end="2024-01")
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")

    facets: dict[str, list[str]] = {}
    if states := as_list(state):
        facets["duoarea"] = [f"S{s.upper()}" for s in states]

    params = build_params(
        data=["value"], facets=facets, frequency=frequency, start=start, end=end
    )
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("production", route), params
    )
