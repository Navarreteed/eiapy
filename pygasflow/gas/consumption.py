"""Natural gas consumption (``/natural-gas/cons/``)."""

from __future__ import annotations

import pandas as pd

from ..client import EIAClient
from ..routes import resolve_route
from ..utils import as_list, build_params, validate_date, validate_frequency


def get_consumption(
    state: str | list[str] | None = None,
    *,
    route: str | None = None,
    frequency: str = "monthly",
    start: str | None = None,
    end: str | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch natural gas consumption data.

    Pulls from the EIA endpoint ``/natural-gas/cons/sum``. All matching
    rows are returned (the client paginates automatically beyond the
    EIA's 5,000-row-per-request cap).

    Args:
        state: U.S. state abbreviation (e.g. ``"TX"``) or list of
            abbreviations. ``None`` returns all areas.
        frequency: Periodicity. One of ``"monthly"``, ``"quarterly"``,
            ``"annual"``. Defaults to ``"monthly"``.
        start: Start of date range, e.g. ``"2020-01"``.
        end: End of date range, e.g. ``"2024-01"``.
        api_key: EIA API key. If omitted, ``EIA_API_KEY`` is read from
            the environment.

    Returns:
        DataFrame of consumption rows. Columns include ``period``,
        ``duoarea``, ``process``, ``series``, ``value`` and ``units``.

    Example:
        >>> from pygasflow import get_consumption
        >>> df = get_consumption(state="TX", frequency="monthly",
        ...                      start="2020-01", end="2024-01")
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
        resolve_route("consumption", route), params
    )
