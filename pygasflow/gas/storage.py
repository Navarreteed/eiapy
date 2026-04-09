"""Natural gas storage (``/natural-gas/stor/``)."""

from __future__ import annotations

import pandas as pd

from ..client import EIAClient
from ..routes import resolve_route
from ..utils import as_list, build_params, validate_date, validate_frequency

_REGION_MAP = {
    "east": "R31",
    "midwest": "R32",
    "mountain": "R34",
    "pacific": "R35",
    "south_central": "R33",
    "lower48": "NUS",
    "national": "NUS",
}


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

    Pulls from the EIA endpoint ``/natural-gas/stor/wkly``. Storage data
    is published weekly by EIA.

    Args:
        region: One of ``"east"``, ``"midwest"``, ``"mountain"``,
            ``"pacific"``, ``"south_central"``, ``"lower48"``/
            ``"national"``, or a list of those. ``None`` returns all.
        frequency: ``"weekly"`` (default) — storage is reported weekly.
        start: Start of date range, e.g. ``"2023-01"``.
        end: End of date range.
        api_key: EIA API key (defaults to ``EIA_API_KEY``).

    Returns:
        DataFrame of storage rows. Columns include ``period``,
        ``duoarea``, ``series``, ``value`` (billion cubic feet)
        and ``units``.

    Example:
        >>> from pygasflow import get_storage
        >>> df = get_storage(region="east", frequency="weekly")
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

    params = build_params(facets=facets, frequency=frequency, start=start, end=end)
    return EIAClient(api_key=api_key).fetch_all(
        resolve_route("storage", route), params
    )
