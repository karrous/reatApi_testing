"""Write operations (POST/PUT/PATCH/DELETE) across all six resources.

JSONPlaceholder accepts writes but never persists them, so each test asserts
only on the response of the call itself.
"""

import pytest

from data import RESOURCES, WRITE_DATA, next_id
from helpers import assert_status, get_json


@pytest.mark.parametrize("resource", RESOURCES)
def test_post_creates_resource_with_echoed_fields_and_next_id(api_client, resource):
    payload, _ = WRITE_DATA[resource]
    body = get_json(api_client.post(f"/{resource}", json=payload), 201)
    assert body == {**payload, "id": next_id(resource)}


@pytest.mark.parametrize("resource", RESOURCES)
def test_put_replaces_resource_and_echoes_body(api_client, resource):
    payload, _ = WRITE_DATA[resource]
    body = get_json(api_client.put(f"/{resource}/1", json=payload))
    assert body == {**payload, "id": 1}


@pytest.mark.parametrize("resource", RESOURCES)
def test_patch_changes_only_the_patched_field(api_client, resource):
    _, field = WRITE_DATA[resource]
    original = get_json(api_client.get(f"/{resource}/1"))
    body = get_json(api_client.patch(f"/{resource}/1", json={field: "patched"}))
    assert body == {**original, field: "patched"}


@pytest.mark.parametrize("resource", RESOURCES)
def test_delete_returns_200_and_empty_object(api_client, resource):
    assert get_json(api_client.delete(f"/{resource}/1")) == {}


@pytest.mark.negative
@pytest.mark.parametrize("resource", RESOURCES)
def test_writes_are_not_persisted(api_client, resource):
    payload, _ = WRITE_DATA[resource]
    created = get_json(api_client.post(f"/{resource}", json=payload), 201)
    assert_status(api_client.get(f"/{resource}/{created['id']}"), 404)


@pytest.mark.negative
@pytest.mark.parametrize("resource", RESOURCES)
def test_post_with_empty_body_is_accepted_and_only_returns_id(api_client, resource):
    # Surprising but observed: no input validation on any resource.
    body = get_json(api_client.post(f"/{resource}", json={}), 201)
    assert body == {"id": next_id(resource)}


@pytest.mark.negative
@pytest.mark.parametrize("resource", RESOURCES)
def test_put_on_nonexistent_id_returns_500(api_client, resource):
    # Observed quirk: an unknown id on PUT yields 500 rather than 404.
    assert_status(api_client.put(f"/{resource}/999999", json={"title": "x"}), 500)
