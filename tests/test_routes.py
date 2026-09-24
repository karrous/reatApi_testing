"""Route discovery: nested routes, unknown routes and non-CRUD HTTP methods."""

import pytest

from helpers import assert_status, get_json, get_non_empty_list

NESTED_ROUTES = [
    ("/posts/1/comments", "postId"),
    ("/albums/1/photos", "albumId"),
    ("/users/1/albums", "userId"),
    ("/users/1/todos", "userId"),
    ("/users/1/posts", "userId"),
]


@pytest.mark.parametrize("path, owner_field", NESTED_ROUTES)
def test_nested_route_returns_only_items_of_parent(api_client, path, owner_field):
    items = get_non_empty_list(api_client.get(path))
    assert all(item[owner_field] == 1 for item in items)


@pytest.mark.parametrize("path, owner_field", NESTED_ROUTES)
def test_nested_route_equals_filtered_list(api_client, path, owner_field):
    child = path.rsplit("/", 1)[1]
    nested = get_json(api_client.get(path))
    filtered = get_json(api_client.get(f"/{child}", params={owner_field: 1}))
    assert nested == filtered


@pytest.mark.negative
@pytest.mark.parametrize("path", ["/unknown", "/posts/1/unknown"])
def test_unknown_route_returns_404(api_client, path):
    assert_status(api_client.get(path), 404)


@pytest.mark.negative
@pytest.mark.parametrize("path", ["/posts/1/comments", "/users/1/todos"])
def test_nested_route_for_nonexistent_parent_returns_empty_list(api_client, path):
    assert get_json(api_client.get(path.replace("/1/", "/999999/"))) == []


def test_head_returns_headers_without_body(api_client):
    resp = api_client.head("/posts/1")
    assert_status(resp, 200)
    assert resp.headers["Content-Type"].startswith("application/json")
    assert resp.content == b""


def test_cors_preflight_allows_all_crud_methods(api_client):
    resp = api_client.options(
        "/posts/1",
        headers={"Origin": "http://example.com", "Access-Control-Request-Method": "DELETE"},
    )
    assert_status(resp, 204)
    assert resp.headers["Access-Control-Allow-Origin"] == "http://example.com"
    allowed = {m.strip() for m in resp.headers["Access-Control-Allow-Methods"].split(",")}
    assert {"GET", "POST", "PUT", "PATCH", "DELETE"} <= allowed


def test_cors_header_echoes_request_origin(api_client):
    resp = api_client.get("/posts/1", headers={"Origin": "http://example.com"})
    assert_status(resp, 200)
    assert resp.headers["Access-Control-Allow-Origin"] == "http://example.com"
