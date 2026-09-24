"""/posts specifics: author filter, nested comments, relations and id handling.

Generic list/get/schema/CRUD checks for posts live in test_contract.py and
test_crud.py, which run them against every resource.
"""

import pytest
from jsonschema import validate

from helpers import assert_status, get_json, get_non_empty_list
from schemas import COMMENT_SCHEMA


def test_get_posts_filtered_by_user_id_returns_only_that_users_posts(api_client):
    posts = get_non_empty_list(api_client.get("/posts", params={"userId": 1}))
    assert len(posts) == 10
    assert all(p["userId"] == 1 for p in posts)


def test_get_posts_filter_with_no_match_returns_empty_list(api_client):
    assert get_json(api_client.get("/posts", params={"userId": 999})) == []


def test_get_post_comments_returns_comments_for_that_post(api_client):
    comments = get_non_empty_list(api_client.get("/posts/1/comments"))
    assert len(comments) == 5
    for comment in comments:
        validate(comment, COMMENT_SCHEMA)
        assert comment["postId"] == 1


def test_every_post_belongs_to_an_existing_user(fetch_list):
    user_ids = {u["id"] for u in fetch_list("users")}
    assert {p["userId"] for p in fetch_list("posts")} <= user_ids


def test_every_comment_belongs_to_an_existing_post(fetch_list):
    post_ids = {p["id"] for p in fetch_list("posts")}
    assert {c["postId"] for c in fetch_list("comments")} <= post_ids


@pytest.mark.negative
@pytest.mark.parametrize("post_id", ["-1", "0", "abc", "1.5"])
def test_get_post_with_malformed_id_returns_404(api_client, post_id):
    # A strict API would return 400 for a malformed id; JSONPlaceholder returns 404.
    assert_status(api_client.get(f"/posts/{post_id}"), 404)
