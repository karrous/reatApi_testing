"""Server-side query features: pagination, slicing, sorting, search, relations.

Unlike writes, these are really implemented by JSONPlaceholder (json-server),
so every result is checked against the full list, not just its shape.
"""

import pytest

from helpers import get_json, get_non_empty_list


def ids(items: list) -> list:
    return [item["id"] for item in items]


@pytest.mark.parametrize("page, limit", [(1, 10), (2, 10), (3, 7)])
def test_pagination_returns_the_requested_page(api_client, fetch_list, page, limit):
    resp = api_client.get("/posts", params={"_page": page, "_limit": limit})
    start = (page - 1) * limit
    assert ids(get_json(resp)) == ids(fetch_list("posts")[start : start + limit])


def test_pagination_reports_total_count_and_links(api_client):
    resp = api_client.get("/posts", params={"_page": 2, "_limit": 10})
    get_json(resp)
    assert resp.headers["X-Total-Count"] == "100"
    assert {"first", "prev", "next", "last"} <= set(resp.links)


@pytest.mark.negative
def test_page_past_the_end_returns_empty_list(api_client):
    assert get_json(api_client.get("/posts", params={"_page": 999, "_limit": 10})) == []


def test_limit_caps_the_number_of_items(api_client):
    assert ids(get_json(api_client.get("/posts", params={"_limit": 5}))) == [1, 2, 3, 4, 5]


def test_start_end_returns_slice(api_client, fetch_list):
    resp = api_client.get("/posts", params={"_start": 10, "_end": 15})
    assert ids(get_json(resp)) == ids(fetch_list("posts")[10:15])


@pytest.mark.parametrize("order", ["asc", "desc"])
def test_sort_by_string_field(api_client, fetch_list, order):
    users = get_non_empty_list(api_client.get("/users", params={"_sort": "name", "_order": order}))
    expected = sorted(fetch_list("users"), key=lambda u: u["name"], reverse=order == "desc")
    assert [u["name"] for u in users] == [u["name"] for u in expected]


def test_sort_desc_with_limit_returns_highest_ids(api_client):
    resp = api_client.get("/posts", params={"_sort": "id", "_order": "desc", "_limit": 3})
    assert ids(get_json(resp)) == [100, 99, 98]


def test_range_operators(api_client):
    resp = api_client.get("/posts", params={"id_gte": 98, "id_lte": 99})
    assert ids(get_json(resp)) == [98, 99]


def test_full_text_search_matches_only_items_containing_the_term(api_client, fetch_list):
    term = "qui est esse"
    expected = [p for p in fetch_list("posts") if any(term in str(v) for v in p.values())]
    assert get_non_empty_list(api_client.get("/posts", params={"q": term})) == expected


def test_embed_includes_child_resources(api_client):
    post = get_json(api_client.get("/posts/1", params={"_embed": "comments"}))
    expected = get_json(api_client.get("/posts/1/comments"))
    assert post["comments"] == expected


def test_expand_includes_parent_resource(api_client):
    post = get_json(api_client.get("/posts/1", params={"_expand": "user"}))
    assert post["user"] == get_json(api_client.get(f"/users/{post['userId']}"))
