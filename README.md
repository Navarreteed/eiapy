# pygasflow

Clean Python access to EIA natural gas data. One-line calls that return complete, typed pandas DataFrames — pagination, authentication, retries, and parameter mapping all handled for you.

```python
from pygasflow import get_consumption, get_movements, list_routes

# Consumption summary (natural-gas/cons/sum) — default behavior unchanged
df = get_consumption(state="TX", frequency="monthly", start="2023-01")

# New: target any sub-route with the route= parameter
df = get_consumption(state="TX", route="heat")   # heat content deliveries
df = get_consumption(state="CA", route="pns")    # pipeline & storage
df = get_movements(route="impc")                 # imports by country
df = get_movements(route="expc")                 # exports by country

# Discover everything available
list_routes("consumption")
# {'consumption': ['acct', 'heat', 'num', 'pns', 'sum']}

list_routes()
# {'consumption': [...], 'movements': [...], 'production': [...], ...}
```

---

## Installation

```bash
pip install pygasflow
```

**Requires Python 3.10+** and a free EIA API key from <https://www.eia.gov/opendata/register.php>.

Set the key before calling any function:

```bash
export EIA_API_KEY="your_key_here"
```

Or pass it directly: `get_consumption(api_key="your_key_here")`.

---

## Available functions

| Function | Default route | Group variants |
|---|---|---|
| `get_consumption()` | `cons/sum` | `sum`, `num`, `pns`, `acct`, `heat` |
| `get_movements()` | `move/ist` | `ist`, `impc`, `expc`, `state`, `poe1`, `poe2` |
| `get_production()` | `prod/sum` | `sum`, `oilwells`, `whv`, `off`, `deep`, `ngpl`, `lc`, `coalbed`, `shalegas`, `ss`, `wells`, `pp` |
| `get_storage()` | `stor/wkly` | `wkly`, `sum`, `type`, `lng`, `cap` |
| `get_prices()` | `pri/sum` | `sum`, `fut`, `rescom` |
| `get_summary()` | `sum/lsum` | `lsum`, `snd`, `sndm` |
| `get_exploration()` | `enr/sum` | `sum`, `cplc`, `dry`, `wals`, `nang`, `adng`, `ngl`, `ngpl`, `lc`, `coalbed`, `shalegas`, `deep`, `nprod`, `drill`, `wellend`, `seis`, `wellfoot`, `welldep`, `wellcost` |

All functions share the same keyword arguments:

```python
get_consumption(
    state=None,           # "TX" or ["TX", "CA"] — None returns all areas
    *,
    route=None,           # sub-route variant, e.g. "heat" — None = default
    frequency="monthly",  # "daily" | "weekly" | "monthly" | "quarterly" | "annual"
    start=None,           # "YYYY", "YYYY-MM", or "YYYY-MM-DD"
    end=None,
    api_key=None,         # falls back to EIA_API_KEY env var
)
```

`get_storage()` uses `region=` instead of `state=` and defaults to `frequency="weekly"`.
`get_exploration()` defaults to `frequency="annual"`.
`get_summary()` has no area filter.

---

## Route selection

Every function accepts a `route` keyword that selects a sub-route within its group. Omitting it (or passing `None`) preserves the original default behavior.

```python
from pygasflow import get_movements, list_routes, resolve_route

# See what's available
list_routes("movements")
# {'movements': ['expc', 'impc', 'ist', 'poe1', 'poe2', 'state']}

# Resolve to the full EIA path
resolve_route("movements", "impc")
# 'natural-gas/move/impc'

# Use it
df = get_movements(route="expc", frequency="annual", start="2015")
```

An invalid variant raises `ValueError` listing the valid options.

---

## Metadata inspection

```python
from pygasflow import get_available_series

# Pass a group name — returns metadata for its default route
meta = get_available_series("consumption")

# Or pass a raw EIA route
meta = get_available_series("natural-gas/cons/heat")

print(meta.get("description"))
print([f["id"] for f in meta.get("facets", [])])
print([f["id"] for f in meta.get("frequency", [])])
```

---

## Examples

```python
from pygasflow import (
    get_consumption, get_exploration, get_movements,
    get_prices, get_production, get_storage, get_summary,
)

# Monthly Texas consumption summary
df = get_consumption(state="TX", frequency="monthly", start="2020-01", end="2024-12")

# Heat content of gas deliveries to all states, annual
df = get_consumption(route="heat", frequency="annual", start="2010")

# Interstate pipeline flows, annual
df = get_movements(route="ist", frequency="annual")

# Natural gas imports by country of origin
df = get_movements(route="impc", frequency="annual", start="2015")

# Exports through pipeline points of exit
df = get_movements(route="expc")

# Weekly storage — east region
df = get_storage(region="east", frequency="weekly", start="2023-01")

# LNG storage capacity
df = get_storage(route="lng", frequency="annual")

# Spot and futures prices
df = get_prices(route="fut", frequency="monthly", start="2020-01")

# Shale gas production in Pennsylvania
df = get_production(state="PA", route="shalegas", frequency="annual")

# Exploration: wells drilled by state
df = get_exploration(state="TX", route="drill", frequency="annual", start="2000")

# Exploration: shale gas reserves
df = get_exploration(route="shalegas", frequency="annual")
```

---

## Error handling

```python
from pygasflow import (
    get_consumption,
    MissingAPIKeyError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    RequestFailedError,
)

try:
    df = get_consumption(state="TX")
except MissingAPIKeyError:
    print("Set EIA_API_KEY first.")
except AuthenticationError:
    print("Invalid API key.")
except RateLimitError:
    print("Slow down — EIA rate limit hit.")
except RequestFailedError as e:
    print(f"Request failed: {e} (HTTP {e.status_code})")
```

---

## Route discovery script

`scripts/discover_routes.py` crawls the EIA metadata tree and enumerates all leaf routes under any root. The 53 routes currently registered were discovered this way:

```bash
python scripts/discover_routes.py natural-gas
```

Output is printed to stdout and written to `scripts/discovered_natural-gas.json`.

---

## License

MIT
