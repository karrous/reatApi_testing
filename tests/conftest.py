import pytest

from api_client import ApiClient
from helpers import get_non_empty_list


@pytest.fixture(scope="session")
def api_client():
    client = ApiClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def fetch_list(api_client):
    """GET /{resource} once per session and reuse it (the dataset is static and /photos is 5000 items)."""
    cache: dict[str, list] = {}

    def _fetch(resource: str) -> list:
        if resource not in cache:
            cache[resource] = get_non_empty_list(api_client.get(f"/{resource}"))
        return cache[resource]

    return _fetch
