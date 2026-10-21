"""The offline suite selects its own baseline; a developer's demo mode is not test data."""
import pytest

from app.providers.registry import get_selected_provider


@pytest.fixture(autouse=True)
def isolate_default_provider(monkeypatch):
    monkeypatch.setenv("AUCTION_PROVIDER", "fixture")
    get_selected_provider.cache_clear()
    yield
    get_selected_provider.cache_clear()
