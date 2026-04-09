"""Shared pytest fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch):
    """Ensure tests run with a deterministic API key."""
    monkeypatch.setenv("EIA_API_KEY", "TEST_KEY")
    yield


@pytest.fixture
def base_url() -> str:
    return "https://api.eia.gov/v2/"
