"""Tests for the RouteRegistry and route resolution."""

import pytest

from eiapy.routes import REGISTRY, RouteInfo, resolve_route, list_routes


class TestRouteRegistry:
    def test_list_categories_includes_all(self):
        cats = REGISTRY.list_categories()
        assert "natural-gas" in cats
        assert "electricity" in cats
        assert "petroleum" in cats
        assert "coal" in cats
        assert len(cats) == 13

    def test_list_groups_natural_gas(self):
        groups = REGISTRY.list_groups("natural-gas")
        assert "cons" in groups
        assert "prod" in groups
        assert "stor" in groups
        assert "pri" in groups
        assert "move" in groups
        assert "enr" in groups
        assert "sum" in groups

    def test_resolve_natural_gas_route(self):
        path = REGISTRY.resolve("natural-gas", "cons", "sum")
        assert path == "natural-gas/cons/sum"

    def test_resolve_electricity_route(self):
        groups = REGISTRY.list_groups("electricity")
        first_group = next(iter(groups))
        first_variant = groups[first_group][0]
        path = REGISTRY.resolve("electricity", first_group, first_variant)
        assert path.startswith("electricity/")

    def test_resolve_unknown_category_raises(self):
        with pytest.raises(ValueError, match="Unknown category"):
            REGISTRY.resolve("fake-category", "group")

    def test_resolve_unknown_group_raises(self):
        with pytest.raises(ValueError, match="Unknown route group"):
            REGISTRY.resolve("natural-gas", "nonexistent")

    def test_resolve_unknown_variant_raises(self):
        with pytest.raises(ValueError, match="Unknown variant"):
            REGISTRY.resolve("natural-gas", "cons", "nonexistent")

    def test_get_route_info_returns_route_info(self):
        info = REGISTRY.get_route_info("natural-gas", "cons", "sum")
        assert isinstance(info, RouteInfo)
        assert info.path == "natural-gas/cons/sum"
        assert isinstance(info.frequencies, list)
        assert isinstance(info.facets, list)

    def test_all_categories_have_groups(self):
        for cat in REGISTRY.list_categories():
            groups = REGISTRY.list_groups(cat)
            assert len(groups) > 0, f"Category {cat} has no groups"


class TestLegacyResolveRoute:
    def test_resolve_consumption(self):
        assert resolve_route("consumption") == "natural-gas/cons/sum"

    def test_resolve_production(self):
        assert resolve_route("production") == "natural-gas/prod/sum"

    def test_resolve_storage(self):
        assert resolve_route("storage") == "natural-gas/stor/wkly"

    def test_resolve_prices(self):
        assert resolve_route("prices") == "natural-gas/pri/sum"

    def test_resolve_movements(self):
        assert resolve_route("movements") == "natural-gas/move/ist"

    def test_resolve_exploration(self):
        assert resolve_route("exploration") == "natural-gas/enr/sum"

    def test_resolve_summary(self):
        assert resolve_route("summary") == "natural-gas/sum/lsum"

    def test_resolve_with_variant(self):
        assert resolve_route("consumption", "num") == "natural-gas/cons/num"

    def test_unknown_group_raises(self):
        with pytest.raises(ValueError):
            resolve_route("nonexistent")


class TestLegacyListRoutes:
    def test_list_all(self):
        routes = list_routes()
        assert "consumption" in routes
        assert "prices" in routes
        assert isinstance(routes["consumption"], list)
        assert "sum" in routes["consumption"]

    def test_list_single_group(self):
        routes = list_routes("storage")
        assert "storage" in routes
        assert "wkly" in routes["storage"]

    def test_unknown_group_raises(self):
        with pytest.raises(ValueError):
            list_routes("nonexistent")
