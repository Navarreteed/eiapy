"""Natural gas exploration & reserves (``/natural-gas/enr/``)."""

from __future__ import annotations

import pandas as pd

from ..client import EIAClient
from ..routes import resolve_route
from ..utils import as_list, build_params, validate_date, validate_frequency


def get_exploration(
    state: str | list[str] | None = None,
    *,
    route: str | None = None,
    frequency: str = "annual",
    start: str | None = None,
    end: str | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch natural gas exploration and reserves data.

    Pulls from the EIA ``/natural-gas/enr/`` family of endpoints.
    Most sub-routes are annual; ``"drill"`` and ``"wellend"`` also
    support monthly; ``"seis"`` is monthly-only.

    Args:
        state: U.S. state abbreviation (e.g. ``"TX"``) or list of
            abbreviations. ``None`` returns all areas.
        route: Sub-route variant. Defaults to ``"sum"`` (exploration
            summary). Other options: ``"cplc"``, ``"dry"``, ``"wals"``,
            ``"nang"``, ``"adng"``, ``"ngl"``, ``"ngpl"``, ``"lc"``,
            ``"coalbed"``, ``"shalegas"``, ``"deep"``, ``"nprod"``,
            ``"drill"``, ``"wellend"``, ``"seis"``, ``"wellfoot"``,
            ``"welldep"``, ``"wellcost"``.
        frequency: ``"annual"`` (default), ``"monthly"`` (not all routes).
        start: Start of date range, e.g. ``"2015"``.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame with columns including ``period``, ``duoarea``,
        ``process``, ``series``, ``value`` and ``units``.

    Example:
        >>> from pygasflow import get_exploration
        >>> df = get_exploration(state="TX", route="shalegas",
        ...                      frequency="annual", start="2010")
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")

    facets: dict[str, list[str]] = {}
    if states := as_list(state):
        facets["duoarea"] = [f"S{s.upper()}" for s in states]

    params = build_params(facets=facets, frequency=frequency, start=start, end=end)
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("exploration", route), params
    )
