"""Tests for natural gas convenience functions (migrated from test_pygasflow.py)."""

import json
from urllib.parse import parse_qs, urlparse

import pandas as pd
import pytest
import responses

import eiapy
from eiapy import (
    MissingAPIKeyError,
    AuthenticationError,
    NotFoundError,
    get_available_series,
    get_consumption,
    get_exploration,
    get_movements,
    get_prices,
    get_production,
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
    from eiapy.client import EIAClient

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
    sent = parse_qs(urlparse(responses.calls[0].request.url).query)
    assert sent["facets[duoarea][]"] == ["R31"]


def test_get_storage_invalid_region():
    with pytest.raises(ValueError, match="Unknown storage region"):
        get_storage(region="atlantis")


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


@responses.activate
def test_pagination_fetches_all_pages(base_url):
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


# ---------------------------------------------------------------------------
# state=None / no-filter
# ---------------------------------------------------------------------------

_ALL_STATE_ROWS = [
    {"period": "2024-01", "duoarea": "STX", "value": "100"},
    {"period": "2024-01", "duoarea": "SCA", "value": "80"},
    {"period": "2024-01", "duoarea": "NUS", "value": "5000"},
]


@responses.activate
def test_get_production_no_state_sends_no_facet(base_url):
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/prod/sum/data",
        json=_data_payload(_ALL_STATE_ROWS),
    )
    df = get_production()
    assert len(df) == 3
    sent = parse_qs(urlparse(responses.calls[0].request.url).query)
    assert "facets[duoarea][]" not in sent
    assert sent["data[]"] == ["value"]


@responses.activate
def test_get_consumption_no_state_sends_no_facet(base_url):
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/cons/sum/data",
        json=_data_payload(_ALL_STATE_ROWS),
    )
    df = get_consumption()
    assert len(df) == 3
    sent = parse_qs(urlparse(responses.calls[0].request.url).query)
    assert "facets[duoarea][]" not in sent
    assert sent["data[]"] == ["value"]


@responses.activate
def test_get_movements_no_state_sends_no_facet(base_url):
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/move/ist/data",
        json=_data_payload(_ALL_STATE_ROWS),
    )
    df = get_movements()
    assert len(df) == 3
    sent = parse_qs(urlparse(responses.calls[0].request.url).query)
    assert "facets[duoarea][]" not in sent
    assert sent["data[]"] == ["value"]


@responses.activate
def test_get_exploration_no_state_sends_no_facet(base_url):
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/enr/sum/data",
        json=_data_payload(_ALL_STATE_ROWS),
    )
    df = get_exploration()
    assert len(df) == 3
    sent = parse_qs(urlparse(responses.calls[0].request.url).query)
    assert "facets[duoarea][]" not in sent
    assert sent["data[]"] == ["value"]


@responses.activate
def test_get_storage_no_region_sends_no_facet(base_url):
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/stor/wkly/data",
        json=_data_payload(_ALL_STATE_ROWS),
    )
    df = get_storage()
    assert len(df) == 3
    sent = parse_qs(urlparse(responses.calls[0].request.url).query)
    assert "facets[duoarea][]" not in sent
    assert sent["data[]"] == ["value"]
