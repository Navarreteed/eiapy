# eiapy

Python client for the U.S. EIA Open Data API v2. Query **any** energy category -- natural gas, electricity, petroleum, coal, and more -- with one-line calls that return typed pandas DataFrames. Pagination, authentication, retries, and parameter mapping all handled for you.

## Supported categories

| Category | EIA route | Leaf routes |
|---|---|---|
| Coal | `coal` | 13 |
| Crude Oil Imports | `crude-oil-imports` | 1 |
| Densified Biomass | `densified-biomass` | 8 |
| Electricity | `electricity` | 19 |
| International | `international` | 1 |
| Natural Gas | `natural-gas` | 53 |
| Nuclear Outages | `nuclear-outages` | 3 |
| Petroleum | `petroleum` | 112 |
| SEDS | `seds` | 1 |
| STEO | `steo` | 1 |
| Total Energy | `total-energy` | 1 |
| Annual Energy Outlook | `aeo` | 8 |
| Intl. Energy Outlook | `ieo` | 1 |

---

> **Disclaimer:** This package is provided as-is, without any warranties or guarantees. The use of this package, including any data retrieved through it, is entirely the responsibility of the user -- not the developer. Always verify data against official EIA sources before using it in any decision-making or production context.

---

> **Note:** This package is **not currently available on PyPI**. It is under active development. To use it, clone the repository and install it locally (see [Installation](#installation)).

---

## Installation

```bash
git clone https://github.com/Navarreteed/eiapy.git
cd eiapy
pip install -e .
```

**Requires Python 3.10+** and a free EIA API key from <https://www.eia.gov/opendata/register.php>.

```bash
export EIA_API_KEY="your_key_here"
```

Or pass it directly: `get_data(api_key="your_key_here", ...)`.

---

## Quick start

### Generic query -- works with any category

```python
from eiapy import get_data, get_metadata, list_categories, list_groups

# See all 13 categories
list_categories()
# ['aeo', 'coal', 'crude-oil-imports', 'densified-biomass', 'electricity', ...]

# Explore groups within a category
list_groups("electricity")
# {'facility-fuel': [...], 'operating-generator-capacity': [...], 'retail-sales': [...], ...}

# Fetch electricity retail sales data
df = get_data(
    "electricity", "retail-sales",
    facets={"sectorid": "RES", "stateid": "TX"},
    frequency="monthly",
    start="2023-01",
)

# Fetch coal shipment data
df = get_data(
    "coal", "shipments", "receipts",
    facets={"coalRankId": ["BIT"]},
    frequency="annual",
    start="2020",
)

# Fetch petroleum prices
df = get_data("petroleum", "pri", "gnd")

# Discover available facets and frequencies for any endpoint
meta = get_metadata("electricity", "retail-sales")
print([f["id"] for f in meta["facets"]])
```

### Natural gas convenience functions

The original natural-gas-specific API is preserved:

```python
from eiapy import get_consumption, get_storage, get_prices, list_routes

# Same API as before
df = get_consumption(state="TX", frequency="monthly", start="2023-01")
df = get_storage(region="east", frequency="weekly")
df = get_prices(area="national", frequency="annual")

# Route discovery for natural gas
list_routes("consumption")
# {'consumption': ['acct', 'heat', 'num', 'pns', 'sum']}
```

---

## Two-tier API

| Tier | Function | Facets | Best for |
|---|---|---|---|
| **Generic** | `get_data("electricity", "retail-sales", facets={"sectorid": ["RES"]})` | Raw EIA values | Any category |
| **Convenience** | `get_consumption(state="TX")` | Friendly params, auto-mapped | Natural gas |

The generic tier gives you immediate access to **all 222 leaf routes** across all 13 categories. Convenience functions add ergonomic parameter mapping and are currently available for natural gas (more coming).

---

## Available natural gas functions

| Function | Default route | Description |
|---|---|---|
| `get_consumption()` | `cons/sum` | Consumption by sector and state |
| `get_movements()` | `move/ist` | Pipeline flows, imports, exports |
| `get_production()` | `prod/sum` | Dry production by source and state |
| `get_storage()` | `stor/wkly` | Underground and LNG storage levels |
| `get_prices()` | `pri/sum` | Wellhead, spot, and consumer prices |
| `get_summary()` | `sum/lsum` | Supply and disposition summary |
| `get_exploration()` | `enr/sum` | Drilling activity, reserves, wells |

All share the same keyword arguments:

```python
get_consumption(
    state=None,           # "TX" or ["TX", "CA"] -- None returns all areas
    *,
    route=None,           # sub-route variant, e.g. "heat"
    frequency="monthly",  # "daily" | "weekly" | "monthly" | "quarterly" | "annual"
    start=None,           # "YYYY", "YYYY-MM", or "YYYY-MM-DD"
    end=None,
    api_key=None,         # falls back to EIA_API_KEY env var
)
```

**Notes:**
- `get_storage()` uses `region=` instead of `state=` and defaults to `frequency="weekly"`.
- `get_exploration()` defaults to `frequency="annual"`.
- `get_summary()` has no area filter.

---

## Error handling

```python
from eiapy import (
    get_data,
    MissingAPIKeyError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    RequestFailedError,
)

try:
    df = get_data("electricity", "retail-sales")
except MissingAPIKeyError:
    print("Set EIA_API_KEY first.")
except AuthenticationError:
    print("Invalid API key.")
except RateLimitError:
    print("Slow down -- EIA rate limit hit.")
except NotFoundError:
    print("Route not found.")
except RequestFailedError as e:
    print(f"Request failed: {e} (HTTP {e.status_code})")
```

---

## Route discovery script

`scripts/discover_routes.py` crawls the EIA metadata tree to enumerate all leaf routes:

```bash
# Discover routes for a single category
python scripts/discover_routes.py electricity

# Discover all 13 categories at once
python scripts/discover_routes.py --all --output-dir eiapy/_route_data/
```

---

## License

MIT
