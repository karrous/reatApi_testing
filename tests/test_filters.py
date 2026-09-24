"""Query-parameter filtering (single and multiple parameters)."""

import pytest

from helpers import get_json, get_non_empty_list


@pytest.mark.parametrize(
    "path, params, field, value",
    [
        ("/comments", {"postId": 1}, "postId", 1),
        ("/albums", {"userId": 1}, "userId", 1),
        ("/photos", {"albumId": 1}, "albumId", 1),
        ("/todos", {"userId": 1}, "userId", 1),
    ],
)
def test_single_param_filter_returns_only_matching_items(api_client, path, params, field, value):
    items = get_non_empty_list(api_client.get(path, params=params))
    assert all(item[field] == value for item in items)


def test_filter_returns_every_matching_item(api_client, fetch_list):
    expected = [c for c in fetch_list("comments") if c["postId"] == 1]
    assert get_json(api_client.get("/comments", params={"postId": 1})) == expected


def test_todos_multi_param_filter_applies_both_conditions(api_client, fetch_list):
    todos = get_non_empty_list(api_client.get("/todos", params={"userId": 1, "completed": "true"}))
    expected = [t for t in fetch_list("todos") if t["userId"] == 1 and t["completed"] is True]
    assert todos == expected
