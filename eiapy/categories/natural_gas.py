"""Natural gas convenience functions.

These wrap the generic query layer with friendly parameter names
(``state``, ``region``, ``area``) and automatic facet-value mapping
(e.g. ``state="TX"`` -> ``duoarea=STX``).
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..client import EIAClient
from ..routes import resolve_route
from ..utils import as_list, build_params, validate_date, validate_frequency

# ── Facet value maps ─────────────────────────────────────────────────

_REGION_MAP = {
    "east": "R31",
    "midwest": "R32",
    "mountain": "R34",
    "pacific": "R35",
    "south_central": "R33",
    "lower48": "NUS",
    "national": "NUS",
}

_AREA_MAP = {
    "national": "NUS",
    "us": "NUS",
}


# ── Shared helpers ───────────────────────────────────────────────────

def _state_facets(state: str | list[str] | None) -> dict[str, list[str]]:
    facets: dict[str, list[str]] = {}
    if states := as_list(state):
        facets["duoarea"] = [f"S{s.upper()}" for s in states]
    return facets


# ── Public functions ─────────────────────────────────────────────────

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

    Pulls from ``/natural-gas/cons/sum`` by default.

    Args:
        state: U.S. state abbreviation or list. ``None`` returns all.
        route: Sub-route variant (e.g. ``"num"``, ``"pns"``).
        frequency: ``"monthly"`` (default), ``"quarterly"``, ``"annual"``.
        start: Start of date range, e.g. ``"2020-01"``.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame with ``period``, ``duoarea``, ``value``, ``units``, etc.
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")
    params = build_params(
        data=["value"], facets=_state_facets(state),
        frequency=frequency, start=start, end=end,
    )
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("consumption", route), params
    )


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

    Pulls from ``/natural-gas/prod/sum`` by default.

    Args:
        state: U.S. state abbreviation or list. ``None`` returns all.
        route: Sub-route variant (e.g. ``"oilwells"``, ``"shalegas"``).
        frequency: ``"monthly"`` (default), ``"quarterly"``, ``"annual"``.
        start: Start of date range.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame with ``period``, ``duoarea``, ``value``, ``units``, etc.
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")
    params = build_params(
        data=["value"], facets=_state_facets(state),
        frequency=frequency, start=start, end=end,
    )
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("production", route), params
    )


def get_movements(
    state: str | list[str] | None = None,
    *,
    route: str | None = None,
    frequency: str = "annual",
    start: str | None = None,
    end: str | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch interstate natural gas movement / pipeline flows.

    Pulls from ``/natural-gas/move/ist`` by default.

    Args:
        state: U.S. state abbreviation or list. ``None`` returns all.
        route: Sub-route variant (e.g. ``"impc"``, ``"expc"``).
        frequency: ``"monthly"`` (default), ``"quarterly"``, ``"annual"``.
        start: Start of date range.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame with ``period``, ``duoarea``, ``value``, ``units``, etc.
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")
    params = build_params(
        data=["value"], facets=_state_facets(state),
        frequency=frequency, start=start, end=end,
    )
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("movements", route), params
    )


def get_storage(
    region: str | list[str] | None = None,
    *,
    route: str | None = None,
    frequency: str = "weekly",
    start: str | None = None,
    end: str | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch natural gas underground storage levels.

    Pulls from ``/natural-gas/stor/wkly`` by default.

    Args:
        region: One of ``"east"``, ``"midwest"``, ``"mountain"``,
            ``"pacific"``, ``"south_central"``, ``"lower48"``/
            ``"national"``, or a list. ``None`` returns all.
        route: Sub-route variant (e.g. ``"sum"``, ``"lng"``).
        frequency: ``"weekly"`` (default).
        start: Start of date range.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame with ``period``, ``duoarea``, ``value`` (Bcf), etc.
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")

    facets: dict[str, list[str]] = {}
    if regions := as_list(region):
        codes = []
        for r in regions:
            key = r.lower()
            if key not in _REGION_MAP:
                raise ValueError(
                    f"Unknown storage region {r!r}. "
                    f"Valid: {sorted(_REGION_MAP)}."
                )
            codes.append(_REGION_MAP[key])
        facets["duoarea"] = codes

    params = build_params(
        data=["value"], facets=facets,
        frequency=frequency, start=start, end=end,
    )
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("storage", route), params
    )


def get_prices(
    area: str | list[str] | None = None,
    *,
    route: str | None = None,
    frequency: str = "monthly",
    start: str | None = None,
    end: str | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch natural gas prices.

    Pulls from ``/natural-gas/pri/sum`` by default.

    Args:
        area: State abbreviation (e.g. ``"TX"``), ``"national"``/
            ``"us"``, or a list. ``None`` returns all areas.
        route: Sub-route variant (e.g. ``"fut"``, ``"rescom"``).
        frequency: ``"monthly"`` (default), ``"quarterly"``, ``"annual"``.
        start: Start of date range.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame with ``period``, ``duoarea``, ``value`` ($/Mcf), etc.
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")

    facets: dict[str, list[str]] = {}
    if areas := as_list(area):
        codes = []
        for a in areas:
            key = a.lower()
            if key in _AREA_MAP:
                codes.append(_AREA_MAP[key])
            else:
                codes.append(f"S{a.upper()}")
        facets["duoarea"] = codes

    params = build_params(
        data=["value"], facets=facets,
        frequency=frequency, start=start, end=end,
    )
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("prices", route), params
    )


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

    Pulls from ``/natural-gas/enr/sum`` by default.

    Args:
        state: U.S. state abbreviation or list. ``None`` returns all.
        route: Sub-route variant (e.g. ``"shalegas"``, ``"drill"``).
        frequency: ``"annual"`` (default), ``"monthly"`` (some routes).
        start: Start of date range.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame with ``period``, ``duoarea``, ``value``, ``units``, etc.
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")
    params = build_params(
        data=["value"], facets=_state_facets(state),
        frequency=frequency, start=start, end=end,
    )
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("exploration", route), params
    )


def get_summary(
    *,
    route: str | None = None,
    frequency: str = "monthly",
    start: str | None = None,
    end: str | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch the EIA natural gas summary dataset.

    Pulls from ``/natural-gas/sum/lsum`` by default.

    Args:
        route: Sub-route variant (``"lsum"``, ``"snd"``, ``"sndm"``).
        frequency: ``"monthly"`` (default), ``"quarterly"``, ``"annual"``.
        start: Start of date range.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame of summary rows.
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")
    params = build_params(
        data=["value"], frequency=frequency, start=start, end=end,
    )
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("summary", route), params
    )


def get_available_series(
    endpoint: str, *, api_key: str | None = None
) -> dict[str, Any]:
    """List facets and data columns available for a natural gas endpoint.

    Args:
        endpoint: Friendly name (``"consumption"``, ``"prices"``, etc.)
            or a raw EIA route like ``"natural-gas/cons/pns"``.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        Metadata dict with ``frequency``, ``facets``, ``data``, etc.
    """
    # Try resolving as a legacy group name
    try:
        route = resolve_route(endpoint)
    except ValueError:
        route = endpoint
    return EIAClient(api_key=api_key).fetch_metadata(route)
