import os

import pytest

from helpers import assert_status

MAX_RESPONSE_SECONDS = float(os.getenv("API_MAX_RESPONSE_SECONDS", "3"))

pytestmark = pytest.mark.smoke


def test_api_is_reachable(api_client):
    assert_status(api_client.get("/posts/1"), 200)


@pytest.mark.parametrize("path", ["/posts/1", "/posts"])
def test_response_time_is_within_budget(api_client, path):
    resp = api_client.get(path)
    assert_status(resp, 200)
    elapsed = resp.elapsed.total_seconds()
    assert elapsed < MAX_RESPONSE_SECONDS, f"GET {path} took {elapsed:.2f}s (budget {MAX_RESPONSE_SECONDS}s)"
