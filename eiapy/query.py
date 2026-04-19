"""Generic query functions for any EIA v2 API endpoint."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .client import EIAClient
from .routes import REGISTRY
from .utils import build_params, validate_date, validate_frequency


def get_data(
    category: str,
    group: str | None = None,
    variant: str | None = None,
    *,
    route: str | None = None,
    facets: dict[str, str | list[str]] | None = None,
    data: list[str] | None = None,
    frequency: str | None = None,
    start: str | None = None,
    end: str | None = None,
    sort: list[dict[str, str]] | None = None,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Fetch data from any EIA v2 API endpoint.

    This is the universal entry point for querying EIA data.  It works
    with all 13 top-level categories (coal, electricity, natural-gas,
    petroleum, etc.).

    Args:
        category: Top-level EIA category (e.g. ``"electricity"``,
            ``"petroleum"``).  Use ``list_categories()`` to see all.
        group: Route group within the category (e.g. ``"retail-sales"``
            for electricity).  Use ``list_groups(category)`` to see all.
            Can be omitted for flat categories with a single group.
        variant: Specific variant within a group.  Omit to use the
            group's default variant.
        route: Raw EIA route string (e.g. ``"electricity/retail-sales/data"``).
            If provided, *category*, *group*, and *variant* are ignored.
        facets: Dict mapping facet names to values.  Values can be a
            single string or a list of strings.  Use ``get_metadata()``
            to discover available facets for a route.
        data: Data columns to request (defaults to ``["value"]``).
        frequency: One of ``"daily"``, ``"weekly"``, ``"monthly"``,
            ``"quarterly"``, ``"annual"``.
        start: Start of date range (``"YYYY"``, ``"YYYY-MM"`` or
            ``"YYYY-MM-DD"``).
        end: End of date range.
        sort: Sort specification, e.g.
            ``[{"column": "period", "direction": "desc"}]``.
        api_key: EIA API key.  Defaults to ``EIA_API_KEY`` env var.

    Returns:
        DataFrame of result rows.

    Example:
        >>> from eiapy import get_data
        >>> df = get_data(
        ...     "electricity", "retail-sales",
        ...     facets={"sectorid": ["RES"]},
        ...     frequency="monthly",
        ...     start="2023-01",
        ... )
    """
    validate_frequency(frequency)
    validate_date(start, "start")
    validate_date(end, "end")

    # Resolve route and auto-detect data columns from the registry
    default_data: list[str] = ["value"]
    if route is None:
        if group is None:
            groups = REGISTRY.list_groups(category)
            if len(groups) == 1:
                group = next(iter(groups))
            else:
                raise ValueError(
                    f"Category {category!r} has multiple groups: "
                    f"{sorted(groups)}. Please specify a group."
                )
        route = REGISTRY.resolve(category, group, variant)
        if data is None:
            info = REGISTRY.get_route_info(category, group, variant)
            if info.data_columns:
                default_data = info.data_columns

    # Normalise facets: single strings -> lists
    normalised_facets: dict[str, list[str]] | None = None
    if facets:
        normalised_facets = {}
        for k, v in facets.items():
            normalised_facets[k] = [v] if isinstance(v, str) else list(v)

    params = build_params(
        data=data or default_data,
        facets=normalised_facets,
        frequency=frequency,
        start=start,
        end=end,
        sort=sort,
    )
    return EIAClient(api_key=api_key).fetch_all(route, params)


def get_metadata(
    category: str,
    group: str | None = None,
    variant: str | None = None,
    *,
    route: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Fetch metadata (frequencies, facets, data columns) for an endpoint.

    Use this to discover what facets and frequencies are available
    before calling ``get_data()``.

    Args:
        category: Top-level EIA category.
        group: Route group within the category.
        variant: Specific variant within a group.
        route: Raw EIA route string.  If provided, other args are ignored.
        api_key: EIA API key.  Defaults to ``EIA_API_KEY`` env var.

    Returns:
        Dict with keys like ``"frequency"``, ``"facets"``, ``"data"``,
        ``"name"``, ``"description"``.

    Example:
        >>> from eiapy import get_metadata
        >>> meta = get_metadata("electricity", "retail-sales")
        >>> [f["id"] for f in meta["facets"]]
        ['stateid', 'sectorid']
    """
    if route is None:
        if group is None:
            groups = REGISTRY.list_groups(category)
            if len(groups) == 1:
                group = next(iter(groups))
            else:
                raise ValueError(
                    f"Category {category!r} has multiple groups: "
                    f"{sorted(groups)}. Please specify a group."
                )
        route = REGISTRY.resolve(category, group, variant)

    return EIAClient(api_key=api_key).fetch_metadata(route)
