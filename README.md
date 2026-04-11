# pygasflow

Clean Python access to EIA natural gas data. One-line calls that return complete, typed pandas DataFrames — pagination, authentication, retries, and parameter mapping all handled for you.

```python
from pygasflow import get_consumption, get_movements, list_routes

# Consumption summary — default route
df = get_consumption(state="TX", frequency="monthly", start="2023-01")

# Target any sub-route with the route= parameter
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

> **Disclaimer:** This package is provided as-is, without any warranties or guarantees. The use of this package, including any data retrieved through it, is entirely the responsibility of the user — not the developer. Always verify data against official EIA sources before using it in any decision-making or production context.

---

> **Note:** This package is **not currently available on PyPI**. It is under active development. To use it, clone the repository and install it locally (see [Installation](#installation)).

---

## Installation

Clone the repository and install locally:

```bash
git clone https://github.com/Navarreteed/pygasflow.git
cd pygasflow
pip install -e .
```

**Requires Python 3.10+** and a free EIA API key from <https://www.eia.gov/opendata/register.php>.

Set the key before calling any function:

```bash
export EIA_API_KEY="your_key_here"
```

Or pass it directly: `get_consumption(api_key="your_key_here")`.

---

## Available functions

| Function | Default route | Description |
|---|---|---|
| `get_consumption()` | `cons/sum` | Natural gas consumption by sector and state |
| `get_movements()` | `move/ist` | Pipeline flows, imports, and exports |
| `get_production()` | `prod/sum` | Dry natural gas production by source and state |
| `get_storage()` | `stor/wkly` | Underground and LNG storage levels |
| `get_prices()` | `pri/sum` | Wellhead, spot, and consumer prices |
| `get_summary()` | `sum/lsum` | Supply and disposition summary tables |
| `get_exploration()` | `enr/sum` | Drilling activity, reserves, and well data |

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

**Function-specific notes:**
- `get_storage()` uses `region=` instead of `state=` and defaults to `frequency="weekly"`.
- `get_exploration()` defaults to `frequency="annual"`.
- `get_summary()` has no area filter.

---

## All available routes

Every function accepts a `route=` keyword to select a sub-route. The default route is used when `route=None`.

### `get_consumption()` — `natural-gas/cons/`

| Route | EIA path | Description |
|---|---|---|
| `"sum"` *(default)* | `natural-gas/cons/sum` | Consumption summary by sector |
| `"num"` | `natural-gas/cons/num` | Number of consumers |
| `"pns"` | `natural-gas/cons/pns` | Pipeline & storage deliveries |
| `"acct"` | `natural-gas/cons/acct` | Gas account — supply and disposition |
| `"heat"` | `natural-gas/cons/heat` | Heat content of deliveries |

### `get_movements()` — `natural-gas/move/`

| Route | EIA path | Description |
|---|---|---|
| `"ist"` *(default)* | `natural-gas/move/ist` | Interstate pipeline flows |
| `"impc"` | `natural-gas/move/impc` | Imports by country of origin |
| `"expc"` | `natural-gas/move/expc` | Exports by country of destination |
| `"state"` | `natural-gas/move/state` | State-to-state movements |
| `"poe1"` | `natural-gas/move/poe1` | Imports by point of entry |
| `"poe2"` | `natural-gas/move/poe2` | Exports by point of exit |

### `get_production()` — `natural-gas/prod/`

| Route | EIA path | Description |
|---|---|---|
| `"sum"` *(default)* | `natural-gas/prod/sum` | Dry production summary |
| `"oilwells"` | `natural-gas/prod/oilwells` | Production from oil wells |
| `"whv"` | `natural-gas/prod/whv` | Marketed production at wellhead |
| `"off"` | `natural-gas/prod/off` | Offshore production |
| `"deep"` | `natural-gas/prod/deep` | Deep well production |
| `"ngpl"` | `natural-gas/prod/ngpl` | Natural gas plant liquids |
| `"lc"` | `natural-gas/prod/lc` | Lease condensate |
| `"coalbed"` | `natural-gas/prod/coalbed` | Coalbed methane |
| `"shalegas"` | `natural-gas/prod/shalegas` | Shale gas production |
| `"ss"` | `natural-gas/prod/ss` | Supplemental gas supplies |
| `"wells"` | `natural-gas/prod/wells` | Number of producing wells |
| `"pp"` | `natural-gas/prod/pp` | Proved reserves |

### `get_storage()` — `natural-gas/stor/`

| Route | EIA path | Description |
|---|---|---|
| `"wkly"` *(default)* | `natural-gas/stor/wkly` | Weekly underground storage |
| `"sum"` | `natural-gas/stor/sum` | Monthly storage summary |
| `"type"` | `natural-gas/stor/type` | Storage by facility type |
| `"lng"` | `natural-gas/stor/lng` | LNG storage |
| `"cap"` | `natural-gas/stor/cap` | Storage capacity |

### `get_prices()` — `natural-gas/pri/`

| Route | EIA path | Description |
|---|---|---|
| `"sum"` *(default)* | `natural-gas/pri/sum` | Price summary (wellhead, city gate, consumer) |
| `"fut"` | `natural-gas/pri/fut` | Futures prices |
| `"rescom"` | `natural-gas/pri/rescom` | Residential and commercial prices |

### `get_summary()` — `natural-gas/sum/`

| Route | EIA path | Description |
|---|---|---|
| `"lsum"` *(default)* | `natural-gas/sum/lsum` | Long-form supply & disposition summary |
| `"snd"` | `natural-gas/sum/snd` | Supply and disposition (annual) |
| `"sndm"` | `natural-gas/sum/sndm` | Supply and disposition (monthly) |

### `get_exploration()` — `natural-gas/enr/`

| Route | EIA path | Description |
|---|---|---|
| `"sum"` *(default)* | `natural-gas/enr/sum` | Exploration summary |
| `"cplc"` | `natural-gas/enr/cplc` | Crude and plant liquids production |
| `"dry"` | `natural-gas/enr/dry` | Dry hole wells |
| `"wals"` | `natural-gas/enr/wals` | Wells by action and location/status |
| `"nang"` | `natural-gas/enr/nang` | Non-associated natural gas |
| `"adng"` | `natural-gas/enr/adng` | Associated-dissolved natural gas |
| `"ngl"` | `natural-gas/enr/ngl` | Natural gas liquids |
| `"ngpl"` | `natural-gas/enr/ngpl` | NGL plant liquids |
| `"lc"` | `natural-gas/enr/lc` | Lease condensate reserves |
| `"coalbed"` | `natural-gas/enr/coalbed` | Coalbed methane reserves |
| `"shalegas"` | `natural-gas/enr/shalegas` | Shale gas reserves |
| `"deep"` | `natural-gas/enr/deep` | Deep well activity |
| `"nprod"` | `natural-gas/enr/nprod` | Non-producing reserves |
| `"drill"` | `natural-gas/enr/drill` | Wells drilled |
| `"wellend"` | `natural-gas/enr/wellend` | Well completions |
| `"seis"` | `natural-gas/enr/seis` | Seismic crew activity |
| `"wellfoot"` | `natural-gas/enr/wellfoot` | Well footage drilled |
| `"welldep"` | `natural-gas/enr/welldep` | Average well depth |
| `"wellcost"` | `natural-gas/enr/wellcost` | Well drilling costs |

---

## Route discovery helpers

```python
from pygasflow import list_routes, resolve_route

# All route groups and their variants
list_routes()
# {
#   'consumption': ['acct', 'heat', 'num', 'pns', 'sum'],
#   'movements':   ['expc', 'impc', 'ist', 'poe1', 'poe2', 'state'],
#   ...
# }

# Just one group
list_routes("production")
# {'production': ['coalbed', 'deep', 'lc', 'ngpl', 'oilwells', 'pp', 'shalegas', 'ss', 'sum', 'wells', 'whv', 'off']}

# Resolve a group + variant to the full EIA path
resolve_route("movements", "impc")
# 'natural-gas/move/impc'

resolve_route("storage")          # no variant → uses the default
# 'natural-gas/stor/wkly'
```

An invalid variant raises `ValueError` listing the valid options.

---

## Metadata inspection

```python
from pygasflow import get_available_series

# Pass a group name — returns metadata for its default route
meta = get_available_series("consumption")

# Or pass a raw EIA route string
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

# --- Consumption ---

# Monthly Texas residential and commercial consumption, 2020–2024
df = get_consumption(state="TX", frequency="monthly", start="2020-01", end="2024-12")

# Heat content of gas deliveries for all states, annual
df = get_consumption(route="heat", frequency="annual", start="2010")

# Number of consumers in California
df = get_consumption(state="CA", route="num", frequency="annual")

# Pipeline & storage deliveries in multiple states
df = get_consumption(state=["TX", "LA", "OK"], route="pns", frequency="monthly")

# --- Movements ---

# Interstate pipeline flows, annual
df = get_movements(route="ist", frequency="annual")

# Natural gas imports by country of origin
df = get_movements(route="impc", frequency="annual", start="2015")

# Exports by country of destination
df = get_movements(route="expc", frequency="annual", start="2015")

# Imports by point of entry
df = get_movements(route="poe1", frequency="monthly", start="2022-01")

# State-to-state movements
df = get_movements(route="state", frequency="annual")

# --- Production ---

# Shale gas production in Pennsylvania, annual
df = get_production(state="PA", route="shalegas", frequency="annual")

# Offshore production summary
df = get_production(route="off", frequency="annual")

# Number of producing natural gas wells by state
df = get_production(route="wells", frequency="annual", start="2010")

# Coalbed methane production
df = get_production(route="coalbed", frequency="annual")

# Natural gas plant liquids production
df = get_production(route="ngpl", frequency="monthly")

# --- Storage ---

# Weekly underground storage levels — east region
df = get_storage(region="east", frequency="weekly", start="2023-01")

# Monthly storage summary for all regions
df = get_storage(route="sum", frequency="monthly", start="2020-01")

# LNG storage capacity
df = get_storage(route="cap", frequency="annual")

# Storage by facility type
df = get_storage(route="type", frequency="monthly")

# --- Prices ---

# Wellhead, city gate, and consumer price summary
df = get_prices(frequency="monthly", start="2020-01")

# Henry Hub natural gas futures prices
df = get_prices(route="fut", frequency="monthly", start="2020-01")

# Residential and commercial prices by state
df = get_prices(route="rescom", frequency="monthly", start="2022-01")

# --- Summary ---

# Monthly supply and disposition table
df = get_summary(route="sndm", frequency="monthly", start="2020-01")

# Annual supply and disposition
df = get_summary(route="snd", frequency="annual")

# Long-form supply and disposition summary
df = get_summary(route="lsum", frequency="annual")

# --- Exploration ---

# Wells drilled by state, annual, since 2000
df = get_exploration(state="TX", route="drill", frequency="annual", start="2000")

# Shale gas proved reserves
df = get_exploration(route="shalegas", frequency="annual")

# Average cost of drilling a natural gas well
df = get_exploration(route="wellcost", frequency="annual")

# Seismic crew activity
df = get_exploration(route="seis", frequency="annual")

# Well completions
df = get_exploration(route="wellend", frequency="annual", start="2005")
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
except NotFoundError:
    print("Route not found.")
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
