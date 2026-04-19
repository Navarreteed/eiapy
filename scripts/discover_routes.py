"""Recursively discover every EIA API route under a given root.

The EIA v2 metadata endpoint returns a JSON payload whose ``response`` field
contains either:

* ``routes``: a list of child nodes (each with an ``id`` and ``name``) — this
  means the current node is a *branch* and has sub-routes to explore, or
* ``frequency`` / ``data`` / ``facets``: this means the current node is a
  *leaf* and actual data can be fetched from ``<route>/data``.

Crawling the tree is the only reliable way to enumerate every route, because
the set of children is not documented anywhere stable.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from eiapy.client import EIAClient
from eiapy.exceptions import EIAError


def _load_dotenv() -> None:
    env = Path(__file__).resolve().parents[1] / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def crawl(root: str = "natural-gas", max_depth: int = 6) -> dict:
    """Walk the metadata tree under *root* and return a nested dict."""
    _load_dotenv()
    client = EIAClient()

    tree: dict = {}
    leaves: list[dict] = []

    def _visit(route: str, depth: int) -> dict:
        node: dict = {"route": route}
        try:
            meta = client.fetch_metadata(route)
        except EIAError as exc:
            node["error"] = str(exc)
            return node

        node["name"] = meta.get("name")
        node["description"] = (meta.get("description") or "").strip()

        children = meta.get("routes") or []
        if children and depth < max_depth:
            node["children"] = {}
            for child in children:
                cid = child.get("id")
                if not cid:
                    continue
                sub_route = f"{route}/{cid}"
                node["children"][cid] = _visit(sub_route, depth + 1)
        else:
            # Leaf: capture the useful bits
            node["leaf"] = True
            node["frequency"] = [
                f.get("id") for f in meta.get("frequency", []) if f.get("id")
            ]
            node["data_columns"] = list((meta.get("data") or {}).keys()) \
                if isinstance(meta.get("data"), dict) \
                else list(meta.get("data") or [])
            node["facets"] = [
                f.get("id") for f in meta.get("facets", []) if f.get("id")
            ]
            leaves.append(node)
        return node

    tree[root] = _visit(root, 0)
    return {"tree": tree, "leaves": leaves}


ALL_CATEGORIES = [
    "coal",
    "crude-oil-imports",
    "densified-biomass",
    "electricity",
    "international",
    "natural-gas",
    "nuclear-outages",
    "petroleum",
    "seds",
    "steo",
    "total-energy",
    "aeo",
    "ieo",
]


def _print_result(root: str, result: dict) -> None:
    print(f"\nDiscovered {len(result['leaves'])} leaf routes under '{root}':\n")
    print("=" * 78)
    for leaf in result["leaves"]:
        print(f"\n{leaf['route']}")
        if leaf.get("description"):
            print(f"  {leaf['description'][:120]}")
        if leaf.get("frequency"):
            print(f"  frequency: {', '.join(leaf['frequency'])}")
        if leaf.get("facets"):
            print(f"  facets:    {', '.join(leaf['facets'])}")
        if leaf.get("data_columns"):
            cols = leaf["data_columns"][:6]
            more = "" if len(leaf["data_columns"]) <= 6 else f" (+{len(leaf['data_columns']) - 6} more)"
            print(f"  data:      {', '.join(cols)}{more}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Discover EIA API routes")
    parser.add_argument("root", nargs="?", default="natural-gas",
                        help="Root category to crawl (default: natural-gas)")
    parser.add_argument("--all", action="store_true",
                        help="Crawl all known EIA categories")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Directory to write JSON files (default: scripts/)")
    args = parser.parse_args()

    out_dir = Path(args.output_dir) if args.output_dir else Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)

    categories = ALL_CATEGORIES if args.all else [args.root]

    for root in categories:
        print(f"\n{'='*78}")
        print(f"Crawling: {root}")
        print(f"{'='*78}")
        result = crawl(root)
        _print_result(root, result)

        slug = root.replace("-", "_")
        out = out_dir / f"{slug}.json"
        out.write_text(json.dumps(result, indent=2, default=str))
        print(f"\nWritten to {out}")


if __name__ == "__main__":
    main()
