"""Integration-style tests for pygasflow using mocked HTTP."""

import json
from urllib.parse import parse_qs, urlparse

import pandas as pd
import pytest
import responses

import pygasflow
from pygasflow import (
    MissingAPIKeyError,
    AuthenticationError,
    NotFoundError,
    get_available_series,
    get_consumption,
    get_prices,
    get_storage,
)


def _data_payload(rows, total=None):
    return {"response": {"total": str(total or len(rows)), "data": rows}}


# ---------------------------------------------------------------------------
# Auth / configuration
# ---------------------------------------------------------------------------


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    with pytest.raises(MissingAPIKeyError):
        get_consumption(state="TX")


def test_explicit_api_key_overrides_env(monkeypatch):
    monkeypatch.setenv("EIA_API_KEY", "ENV_KEY")
    from pygasflow.client import EIAClient

    assert EIAClient(api_key="EXPLICIT").api_key == "EXPLICIT"
    assert EIAClient().api_key == "ENV_KEY"


# ---------------------------------------------------------------------------
# Single-page query
# ---------------------------------------------------------------------------


@responses.activate
def test_get_prices_returns_dataframe(base_url):
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/pri/sum/data",
        json=_data_payload(
            [{"period": "2024-01", "duoarea": "NUS", "value": "3.45"}]
        ),
    )
    df = get_prices(area="national", frequency="annual")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df["value"].dtype.kind == "f"


@responses.activate
def test_get_storage_with_region(base_url):
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/stor/wkly/data",
        json=_data_payload(
            [{"period": "2024-01-05", "duoarea": "R31", "value": "850"}]
        ),
    )
    df = get_storage(region="east", frequency="weekly")
    assert len(df) == 1
    # Confirm the duoarea facet was sent correctly
    sent = parse_qs(urlparse(responses.calls[0].request.url).query)
    assert sent["facets[duoarea][]"] == ["R31"]


def test_get_storage_invalid_region():
    with pytest.raises(ValueError, match="Unknown storage region"):
        get_storage(region="atlantis")


# ---------------------------------------------------------------------------
# Pagination — the critical requirement
# ---------------------------------------------------------------------------


@responses.activate
def test_pagination_fetches_all_pages(base_url):
    """Client must paginate until a partial page is returned."""
    full = [{"period": f"2024-{i:04d}", "value": str(i)} for i in range(5000)]
    partial = [{"period": "tail", "value": "1"}]

    seen_offsets = []

    def callback(request):
        offset = int(parse_qs(urlparse(request.url).query)["offset"][0])
        seen_offsets.append(offset)
        rows = full if offset == 0 else partial
        return (200, {}, json.dumps(_data_payload(rows)))

    responses.add_callback(
        responses.GET,
        f"{base_url}natural-gas/cons/sum/data",
        callback=callback,
        content_type="application/json",
    )

    df = get_consumption(state="TX")
    assert len(df) == 5001
    assert seen_offsets == [0, 5000]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


@responses.activate
def test_401_raises_auth_error(base_url):
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/cons/sum/data",
        status=401,
        body="Unauthorized",
    )
    with pytest.raises(AuthenticationError):
        get_consumption(state="TX")


@responses.activate
def test_404_raises_not_found(base_url):
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/cons/sum",
        status=404,
        body="not found",
    )
    with pytest.raises(NotFoundError):
        get_available_series("consumption")


# ---------------------------------------------------------------------------
# Metadata helper
# ---------------------------------------------------------------------------


@responses.activate
def test_get_available_series(base_url):
    payload = {
        "response": {
            "frequency": [{"id": "monthly"}],
            "facets": [{"id": "duoarea"}, {"id": "process"}],
            "data": {"value": {"alias": "value"}},
        }
    }
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/cons/sum",
        json=payload,
    )
    meta = get_available_series("consumption")
    assert "facets" in meta
    assert any(f["id"] == "duoarea" for f in meta["facets"])
