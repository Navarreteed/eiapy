# Contributing to pygasflow

This document covers architecture, conventions, and how to extend the library.

---

## What this project is

`pygasflow` is a thin Python wrapper around the **EIA OpenData API v2** for natural gas data. The design goal: one-line calls that return complete, typed pandas DataFrames — pagination, auth, retries, and parameter mapping hidden from the caller.

**Version:** 0.1.0 · **Python:** 3.10+

---

## Dev environment setup

```bash
git clone <repo-url>
cd pygasflow
pip install -e ".[dev]"
```

Get a free EIA API key at <https://www.eia.gov/opendata/register.php> and put it in a `.env` file at the repo root (already in `.gitignore`):

```
EIA_API_KEY="your_key_here"
```

Run the test suite (no network access required — all HTTP is mocked):

```bash
pytest
```

---

## Repository layout

```
pygasflow/
├── pygasflow/
│   ├── __init__.py          # Public exports — everything users import
│   ├── client.py            # EIAClient: HTTP, pagination, retries, DataFrame conversion
│   ├── exceptions.py        # Exception hierarchy
│   ├── routes.py            # ROUTE_REGISTRY, resolve_route(), list_routes()
│   ├── utils.py             # Input validation and parameter builders
│   └── gas/
│       ├── __init__.py      # Re-exports from each endpoint module
│       ├── consumption.py   # get_consumption()
│       ├── exploration.py   # get_exploration()
│       ├── movements.py     # get_movements()
│       ├── prices.py        # get_prices()
│       ├── production.py    # get_production()
│       ├── storage.py       # get_storage()
│       └── summary.py       # get_summary(), get_available_series()
├── scripts/
│   ├── discover_routes.py              # Recursive EIA metadata tree crawler
│   └── discovered_natural-gas.json    # Last crawl output (53 leaf routes)
├── tests/
│   ├── conftest.py          # Shared pytest fixtures
│   └── test_pygasflow.py    # Full test suite
└── pyproject.toml
```

---

## Architecture

### Data flow

```
User call  (e.g. get_consumption(state="TX", route="heat"))
    │
    ▼
Endpoint module  (gas/consumption.py)
  - validate inputs (frequency, dates)
  - map user-friendly args to EIA codes ("TX" → "STX")
  - resolve_route("consumption", "heat") → "natural-gas/cons/heat"
  - call EIAClient.fetch_all(route, params)
    │
    ▼
EIAClient  (client.py)
  - resolve API key (param → EIA_API_KEY env var → MissingAPIKeyError)
  - paginate: GET /v2/{route}/data?offset=0, 5000, 10000… until < 5000 rows
  - retry on transient errors (3 attempts, exponential backoff)
  - raise typed exception on HTTP error codes
  - coerce period → datetime, value → numeric
    │
    ▼
pandas.DataFrame returned to caller
```

### Separation of concerns

| Layer | File | Responsibility |
|---|---|---|
| Public API | `__init__.py` | Single import surface |
| Routes | `routes.py` | Route registry, resolution, discovery |
| Endpoint | `gas/*.py` | Validation, arg mapping, route selection |
| HTTP | `client.py` | Requests, pagination, retries, typing |
| Validation | `utils.py` | Date/freq validation, param builders |
| Errors | `exceptions.py` | Typed exception hierarchy |

**Rule:** endpoint modules never call `requests` directly. `client.py` never knows which dataset is being fetched. Keep these layers clean.

---

## Route registry (`routes.py`)

The registry was built by crawling the EIA metadata tree with `scripts/discover_routes.py`. It maps group names → sub-route variants → full EIA paths.

```python
ROUTE_REGISTRY = {
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
    # … six more groups
}
```

Two public helpers are exported from `pygasflow`:

- `resolve_route(group, variant=None)` — returns the full EIA route string
- `list_routes(group=None)` — returns available variants per group

### Re-running route discovery

If the EIA API adds new routes, run the crawler to refresh the registry:

```bash
python scripts/discover_routes.py natural-gas
```

Then update `ROUTE_REGISTRY` in `routes.py` to match the new `discovered_natural-gas.json`.

---

## EIAClient internals (`client.py`)

Only file that touches the network. Key methods:

| Method | What it does |
|---|---|
| `fetch_all(route, params)` | Fetches all pages; loops `_get_page()` until < 5,000 rows come back |
| `fetch_metadata(route)` | Single GET to the metadata endpoint (no `/data` suffix) |
| `_get_page(route, params, offset)` | One paginated request; returns raw response dict |
| `_request(url, params)` | HTTP GET with retry/backoff; raises typed exceptions on errors |

**Pagination:** EIA caps responses at 5,000 rows. `fetch_all` increments `offset` by 5,000 until the response returns fewer than 5,000 rows.

**Retry logic:** up to 3 attempts with exponential backoff. Retries on network errors and 5xx. Raises immediately on 401/403/404/429.

**Type coercion:**
- `period` column → `pd.to_datetime` (best-effort)
- `value` column → `pd.to_numeric` (best-effort)
- All other columns left as-is

---

## Exception hierarchy

```
EIAError
├── MissingAPIKeyError    # No key in param or env var
├── AuthenticationError   # HTTP 401 or 403
├── RateLimitError        # HTTP 429
├── NotFoundError         # HTTP 404
└── RequestFailedError    # Everything else (has .status_code attribute)
```

All exceptions live in `exceptions.py` and are exported from the package root.

---

## Utilities (`utils.py`)

```python
validate_frequency(freq)
# Raises ValueError if freq ∉ {daily, weekly, monthly, quarterly, annual}

validate_date(value, name)
# Raises ValueError if value doesn't match YYYY, YYYY-MM, or YYYY-MM-DD

as_list(value)
# "TX" → ["TX"],  ["TX", "PA"] → ["TX", "PA"],  None → None

build_params(frequency, start, end, facets, data, sort)
# Builds the EIA v2 query-parameter dict (handles multi-value facet format)
```

Always use `build_params` — never construct the query dict by hand.

---

## How to add a new endpoint group

If the EIA API introduces a new category (e.g. `natural-gas/lng/*`):

1. **Run discovery** to find the leaf routes:

   ```bash
   python scripts/discover_routes.py natural-gas/lng
   ```

2. **Add a `RouteGroup`** to `ROUTE_REGISTRY` in `routes.py`:

   ```python
   "lng": RouteGroup(
       default="imports",
       routes={
           "imports": "natural-gas/lng/imports",
           "exports": "natural-gas/lng/exports",
       },
   ),
   ```

3. **Create the endpoint module** at `pygasflow/gas/lng.py`:

   ```python
   from ..client import EIAClient
   from ..routes import resolve_route
   from ..utils import as_list, build_params, validate_date, validate_frequency

   def get_lng(
       state=None,
       *,
       route=None,
       frequency="monthly",
       start=None,
       end=None,
       api_key=None,
   ):
       validate_frequency(frequency)
       validate_date(start, "start")
       validate_date(end, "end")
       facets = {}
       if states := as_list(state):
           facets["duoarea"] = [f"S{s.upper()}" for s in states]
       params = build_params(facets=facets, frequency=frequency, start=start, end=end)
       return EIAClient(api_key=api_key).fetch_all(resolve_route("lng", route), params)
   ```

4. **Export it** — add to `pygasflow/gas/__init__.py` and `pygasflow/__init__.py`.

5. **Write tests** (see Testing section below).

---

## How to add a new sub-route to an existing group

If EIA adds `natural-gas/cons/new_thing`:

1. Add `"new_thing": "natural-gas/cons/new_thing"` to the `"consumption"` entry in `ROUTE_REGISTRY`.
2. That's it — `get_consumption(route="new_thing")` will work immediately.

---

## Testing

**Framework:** `pytest` + [`responses`](https://github.com/getsentry/responses) (HTTP mocking). Tests never hit the real EIA API.

### Fixtures (`conftest.py`)

| Fixture | Scope | What it does |
|---|---|---|
| `_set_api_key` | function, autouse | Sets `EIA_API_KEY=TEST_KEY` for every test |
| `base_url` | function | Returns `"https://api.eia.gov/v2/"` |

### Writing a test

```python
import responses as rsps
from pygasflow import get_consumption

EIA_BASE = "https://api.eia.gov/v2/"

@rsps.activate
def test_consumption_heat_route():
    rsps.add(
        rsps.GET,
        f"{EIA_BASE}natural-gas/cons/heat/data",
        json={
            "response": {
                "total": 2,
                "data": [
                    {"period": "2023-01", "duoarea": "STX", "value": "1200"},
                    {"period": "2023-02", "duoarea": "STX", "value": "1100"},
                ],
            }
        },
        status=200,
    )

    df = get_consumption(state="TX", route="heat", frequency="monthly")
    assert len(df) == 2
    assert df["value"].dtype == float
```

### Checklist for a new endpoint or route

- [ ] Happy path: correct DataFrame shape and types
- [ ] `route=` parameter maps to the correct EIA path (mock the right URL)
- [ ] Invalid route variant raises `ValueError` with helpful message
- [ ] Area/region/state parameter maps to correct EIA facet code
- [ ] HTTP 401 raises `AuthenticationError`
- [ ] Pagination: two mocked pages (5,000 + N rows) return 5,000+N rows total

---

## Conventions

- No `requests` calls outside `client.py`.
- Validate inputs early in endpoint functions, before creating `EIAClient`.
- Map area/region/state codes in the endpoint module, not in the client.
- Use `build_params` for all query-parameter construction.
- Use `resolve_route(group, route)` — never hardcode a route string in an endpoint module.
- `X | None` type hints (not `Optional[X]`).
- Tests mock HTTP — never require a real `EIA_API_KEY` in CI.
- No logging or print statements in library code.

---

## Key EIA API concepts

- **Base URL:** `https://api.eia.gov/v2/`
- **Data endpoint:** `GET /v2/{route}/data?api_key=...&frequency=...&facets[duoarea][]=STX`
- **Metadata endpoint:** `GET /v2/{route}?api_key=...` (no `/data` suffix)
- **Pagination:** `offset` and `length` query params; max `length` is 5,000
- **Response envelope:** `{"response": {"total": N, "data": [...]}}`
- **Facets:** EIA's filterable dimensions (duoarea, product, process, series)

---

## Releasing

1. Bump `version` in `pyproject.toml`.
2. Tag: `git tag v0.x.0`
3. Build: `python -m build`
4. Publish: `twine upload dist/*`

---

## License

MIT
