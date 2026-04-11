"""Natural gas prices (``/natural-gas/pri/``)."""

from __future__ import annotations

import pandas as pd

from ..client import EIAClient
from ..routes import resolve_route
from ..utils import as_list, build_params, validate_date, validate_frequency

_AREA_MAP = {
    "national": "NUS",
    "us": "NUS",
}


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

    Pulls from the EIA endpoint ``/natural-gas/pri/sum``.

    Args:
        area: Either a state abbreviation (e.g. ``"TX"``), the literal
            string ``"national"``/``"us"`` for U.S. totals, or a list
            mixing the two. ``None`` returns all areas.
        frequency: ``"monthly"``, ``"quarterly"`` or ``"annual"``.
        start: Start of date range, e.g. ``"2020-01"``.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame of price rows. Columns typically include ``period``,
        ``duoarea``, ``series``, ``value`` and ``units`` (dollars per
        thousand cubic feet).

    Example:
        >>> from pygasflow import get_prices
        >>> df = get_prices(area="national", frequency="annual")
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
        data=["value"], facets=facets, frequency=frequency, start=start, end=end
    )
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("prices", route), params
    )
