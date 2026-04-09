"""Registry of EIA natural-gas API routes.

The set of leaf routes below was enumerated by crawling the EIA v2
metadata tree under ``natural-gas`` (see ``scripts/discover_routes.py``
and ``scripts/discovered_natural-gas.json``). Each public ``get_*``
function owns one group; within a group, the ``default`` variant is the
one that function used before route selection was added, so passing
``route=None`` preserves the historical behavior.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteGroup:
    default: str
    routes: dict[str, str]


ROUTE_REGISTRY: dict[str, RouteGroup] = {
    "consumption": RouteGroup(
        default="sum",
        routes={
            "sum":  "natural-gas/cons/sum",
            "num":  "natural-gas/cons/num",
            "pns":  "natural-gas/cons/pns",
            "acct": "natural-gas/cons/acct",
            "heat": "natural-gas/cons/heat",
        },
    ),
    "movements": RouteGroup(
        default="ist",
        routes={
            "ist":   "natural-gas/move/ist",
            "impc":  "natural-gas/move/impc",
            "expc":  "natural-gas/move/expc",
            "state": "natural-gas/move/state",
            "poe1":  "natural-gas/move/poe1",
            "poe2":  "natural-gas/move/poe2",
        },
    ),
    "production": RouteGroup(
        default="sum",
        routes={
            "sum":      "natural-gas/prod/sum",
            "oilwells": "natural-gas/prod/oilwells",
            "whv":      "natural-gas/prod/whv",
            "off":      "natural-gas/prod/off",
            "deep":     "natural-gas/prod/deep",
            "ngpl":     "natural-gas/prod/ngpl",
            "lc":       "natural-gas/prod/lc",
            "coalbed":  "natural-gas/prod/coalbed",
            "shalegas": "natural-gas/prod/shalegas",
            "ss":       "natural-gas/prod/ss",
            "wells":    "natural-gas/prod/wells",
            "pp":       "natural-gas/prod/pp",
        },
    ),
    "storage": RouteGroup(
        default="wkly",
        routes={
            "wkly": "natural-gas/stor/wkly",
            "sum":  "natural-gas/stor/sum",
            "type": "natural-gas/stor/type",
            "lng":  "natural-gas/stor/lng",
            "cap":  "natural-gas/stor/cap",
        },
    ),
    "prices": RouteGroup(
        default="sum",
        routes={
            "sum":    "natural-gas/pri/sum",
            "fut":    "natural-gas/pri/fut",
            "rescom": "natural-gas/pri/rescom",
        },
    ),
    "summary": RouteGroup(
        default="lsum",
        routes={
            "lsum": "natural-gas/sum/lsum",
            "snd":  "natural-gas/sum/snd",
            "sndm": "natural-gas/sum/sndm",
        },
    ),
    "exploration": RouteGroup(
        default="sum",
        routes={
            "sum":      "natural-gas/enr/sum",
            "cplc":     "natural-gas/enr/cplc",
            "dry":      "natural-gas/enr/dry",
            "wals":     "natural-gas/enr/wals",
            "nang":     "natural-gas/enr/nang",
            "adng":     "natural-gas/enr/adng",
            "ngl":      "natural-gas/enr/ngl",
            "ngpl":     "natural-gas/enr/ngpl",
            "lc":       "natural-gas/enr/lc",
            "coalbed":  "natural-gas/enr/coalbed",
            "shalegas": "natural-gas/enr/shalegas",
            "deep":     "natural-gas/enr/deep",
            "nprod":    "natural-gas/enr/nprod",
            "drill":    "natural-gas/enr/drill",
            "wellend":  "natural-gas/enr/wellend",
            "seis":     "natural-gas/enr/seis",
            "wellfoot": "natural-gas/enr/wellfoot",
            "welldep":  "natural-gas/enr/welldep",
            "wellcost": "natural-gas/enr/wellcost",
        },
    ),
}


def resolve_route(group: str, variant: str | None = None) -> str:
    """Return the full EIA route string for *group* / *variant*.

    Passing ``variant=None`` yields the group's default route, which
    matches the library's pre-registry behavior.
    """
    try:
        rg = ROUTE_REGISTRY[group]
    except KeyError:
        raise ValueError(
            f"Unknown route group {group!r}. "
            f"Valid groups: {sorted(ROUTE_REGISTRY)}."
        ) from None
    key = variant if variant is not None else rg.default
    try:
        return rg.routes[key]
    except KeyError:
        raise ValueError(
            f"Unknown route variant {variant!r} for {group!r}. "
            f"Valid variants: {sorted(rg.routes)}."
        ) from None


def list_routes(group: str | None = None) -> dict[str, list[str]]:
    """Return available route variants.

    With no argument, returns every group mapped to its variant names.
    With a group name, returns just that group.
    """
    if group is None:
        return {g: sorted(rg.routes) for g, rg in ROUTE_REGISTRY.items()}
    if group not in ROUTE_REGISTRY:
        raise ValueError(
            f"Unknown route group {group!r}. "
            f"Valid groups: {sorted(ROUTE_REGISTRY)}."
        )
    return {group: sorted(ROUTE_REGISTRY[group].routes)}
