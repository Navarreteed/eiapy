"""Internal HTTP client for the EIA OpenData API v2.

Handles authentication, retry on transient errors, and automatic
pagination across the API's 5,000-row-per-request limit.
"""

from __future__ import annotations

import os
import time
from typing import Any
from urllib.parse import urljoin

import pandas as pd
import requests

from .exceptions import (
    AuthenticationError,
    MissingAPIKeyError,
    NotFoundError,
    RateLimitError,
    RequestFailedError,
)

_BASE_URL = "https://api.eia.gov/v2/"
_PAGE_SIZE = 5_000
_TIMEOUT = 30
_MAX_RETRIES = 3


class EIAClient:
    """Thin HTTP wrapper for the EIA v2 API.  Intended for internal use."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("EIA_API_KEY")
        if not self.api_key:
            raise MissingAPIKeyError(
                "No API key provided. Pass api_key=... or set the "
                "EIA_API_KEY environment variable."
            )
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def fetch_all(self, route: str, params: dict[str, Any]) -> pd.DataFrame:
        """Fetch every row matching *params* and return a DataFrame."""
        all_rows: list[dict[str, Any]] = []
        offset = 0
        while True:
            page = self._get_page(route, params, offset=offset, length=_PAGE_SIZE)
            rows = page.get("data", [])
            all_rows.extend(rows)
            if len(rows) < _PAGE_SIZE:
                break
            offset += _PAGE_SIZE
        return _to_dataframe(all_rows)

    def fetch_metadata(self, route: str) -> dict[str, Any]:
        """Return the metadata payload for *route* (no ``/data`` suffix)."""
        url = urljoin(_BASE_URL, route.strip("/"))
        payload = self._request(url, {"api_key": self.api_key})
        return payload.get("response", payload)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_page(
        self, route: str, params: dict[str, Any], *, offset: int, length: int
    ) -> dict[str, Any]:
        url = urljoin(_BASE_URL, f"{route.strip('/')}/data")
        full = {"api_key": self.api_key, "offset": offset, "length": length, **params}
        payload = self._request(url, full)
        return payload.get("response", payload)

    def _request(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        backoff = 1.0
        for attempt in range(_MAX_RETRIES + 1):
            try:
                resp = self._session.get(url, params=params, timeout=_TIMEOUT)
            except requests.RequestException as exc:
                if attempt >= _MAX_RETRIES:
                    raise RequestFailedError(str(exc)) from exc
                time.sleep(backoff)
                backoff *= 2
                continue

            if resp.status_code in (401, 403):
                raise AuthenticationError("Invalid or unauthorised API key.")
            if resp.status_code == 404:
                raise NotFoundError(f"Route not found: {url}")
            if resp.status_code == 429:
                raise RateLimitError("EIA API rate limit exceeded.")
            if resp.status_code >= 500 and attempt < _MAX_RETRIES:
                time.sleep(backoff)
                backoff *= 2
                continue
            if resp.status_code >= 400:
                raise RequestFailedError(
                    f"HTTP {resp.status_code}: {resp.text}",
                    status_code=resp.status_code,
                )

            payload: dict[str, Any] = resp.json()
            if isinstance(payload, dict) and "error" in payload:
                raise RequestFailedError(str(payload["error"]))
            return payload

        raise RequestFailedError("Request failed after retries.")


def _to_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert raw API rows into a typed DataFrame."""
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "period" in df.columns:
        try:
            df["period"] = pd.to_datetime(df["period"])
        except (ValueError, TypeError):
            pass
    if "value" in df.columns:
        try:
            df["value"] = pd.to_numeric(df["value"])
        except (ValueError, TypeError):
            pass
    return df
