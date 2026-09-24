"""Assertion helpers that explain *what* request failed, not just the value."""

import requests

MAX_BODY_CHARS = 500


def describe(resp: requests.Response) -> str:
    body = resp.text
    if len(body) > MAX_BODY_CHARS:
        body = body[:MAX_BODY_CHARS] + "...<truncated>"
    return f"{resp.request.method} {resp.url} -> {resp.status_code}\nResponse body: {body}"


def assert_status(resp: requests.Response, expected: int) -> None:
    assert resp.status_code == expected, f"Expected {expected}.\n{describe(resp)}"


def get_json(resp: requests.Response, expected_status: int = 200):
    """Assert the status code, then return the parsed JSON body."""
    assert_status(resp, expected_status)
    return resp.json()


def get_non_empty_list(resp: requests.Response) -> list:
    """Assert a 200 with a non-empty JSON array, so checks over items can't pass vacuously."""
    body = get_json(resp)
    assert isinstance(body, list), f"Expected a JSON array.\n{describe(resp)}"
    assert body, f"Expected a non-empty array.\n{describe(resp)}"
    return body
