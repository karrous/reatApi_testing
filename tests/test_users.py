"""/users: nested-object details and data integrity.

Schema validation of every user (including nested address/company) runs in
test_contract.py.
"""

from helpers import get_json


def test_user_nested_objects_are_populated(api_client):
    user = get_json(api_client.get("/users/1"))
    assert user["address"]["geo"]["lat"]
    assert user["address"]["geo"]["lng"]
    assert user["company"]["name"]


def test_user_geo_coordinates_are_valid(fetch_list):
    for user in fetch_list("users"):
        geo = user["address"]["geo"]
        assert -90 <= float(geo["lat"]) <= 90, user["id"]
        assert -180 <= float(geo["lng"]) <= 180, user["id"]


def test_user_emails_are_unique(fetch_list):
    emails = [u["email"].lower() for u in fetch_list("users")]
    assert len(emails) == len(set(emails))


def test_usernames_are_unique(fetch_list):
    usernames = [u["username"] for u in fetch_list("users")]
    assert len(usernames) == len(set(usernames))
