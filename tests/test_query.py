"""Tests for the generic get_data() and get_metadata() functions."""

from urllib.parse import parse_qs, urlparse

import pandas as pd
import pytest
import responses

from eiapy import get_data, get_metadata
from eiapy.exceptions import MissingAPIKeyError


def _data_payload(rows, total=None):
    return {"response": {"total": str(total or len(rows)), "data": rows}}


# ---------------------------------------------------------------------------
# get_data()
# ---------------------------------------------------------------------------


@responses.activate
def test_get_data_natural_gas(base_url):
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/cons/sum/data",
        json=_data_payload(
            [{"period": "2024-01", "duoarea": "STX", "value": "100"}]
        ),
    )
    df = get_data(
        "natural-gas", "cons", "sum",
        facets={"duoarea": ["STX"]},
        frequency="monthly",
    )
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    sent = parse_qs(urlparse(responses.calls[0].request.url).query)
    assert sent["facets[duoarea][]"] == ["STX"]


@responses.activate
def test_get_data_electricity(base_url):
    responses.add(
        responses.GET,
        f"{base_url}electricity/retail-sales/data",
        json=_data_payload(
            [{"period": "2024-01", "stateid": "TX", "sectorid": "RES", "value": "500"}]
        ),
    )
    df = get_data(
        "electricity", "retail-sales",
        facets={"sectorid": "RES", "stateid": "TX"},
        frequency="monthly",
    )
    assert len(df) == 1
    sent = parse_qs(urlparse(responses.calls[0].request.url).query)
    assert sent["facets[sectorid][]"] == ["RES"]


@responses.activate
def test_get_data_with_raw_route(base_url):
    responses.add(
        responses.GET,
        f"{base_url}coal/shipments/receipts/data",
        json=_data_payload(
            [{"period": "2024-Q1", "value": "200"}]
        ),
    )
    df = get_data(
        "coal",
        route="coal/shipments/receipts",
        frequency="quarterly",
    )
    assert len(df) == 1


@responses.activate
def test_get_data_single_string_facet_normalised(base_url):
    """A single string facet value should be normalised to a list."""
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/cons/sum/data",
        json=_data_payload(
            [{"period": "2024-01", "value": "100"}]
        ),
    )
    df = get_data(
        "natural-gas", "cons", "sum",
        facets={"duoarea": "STX"},
    )
    assert len(df) == 1
    sent = parse_qs(urlparse(responses.calls[0].request.url).query)
    assert sent["facets[duoarea][]"] == ["STX"]


def test_get_data_invalid_frequency():
    with pytest.raises(ValueError, match="Invalid frequency"):
        get_data("natural-gas", "cons", "sum", frequency="biweekly")


def test_get_data_invalid_date():
    with pytest.raises(ValueError, match="Invalid start"):
        get_data("natural-gas", "cons", "sum", start="not-a-date")


def test_get_data_unknown_category():
    with pytest.raises(ValueError, match="Unknown category"):
        get_data("fake-energy")


def test_get_data_missing_group_multi_group_category():
    with pytest.raises(ValueError, match="multiple groups"):
        get_data("natural-gas")


# ---------------------------------------------------------------------------
# get_metadata()
# ---------------------------------------------------------------------------


@responses.activate
def test_get_metadata(base_url):
    payload = {
        "response": {
            "name": "Consumption Summary",
            "frequency": [{"id": "monthly"}],
            "facets": [{"id": "duoarea"}],
            "data": {"value": {"alias": "value"}},
        }
    }
    responses.add(
        responses.GET,
        f"{base_url}natural-gas/cons/sum",
        json=payload,
    )
    meta = get_metadata("natural-gas", "cons", "sum")
    assert "facets" in meta
    assert meta["name"] == "Consumption Summary"


@responses.activate
def test_get_metadata_with_raw_route(base_url):
    payload = {
        "response": {
            "name": "Coal Receipts",
            "frequency": [{"id": "annual"}],
            "facets": [],
            "data": {},
        }
    }
    responses.add(
        responses.GET,
        f"{base_url}coal/shipments/receipts",
        json=payload,
    )
    meta = get_metadata("coal", route="coal/shipments/receipts")
    assert meta["name"] == "Coal Receipts"
