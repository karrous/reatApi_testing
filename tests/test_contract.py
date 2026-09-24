"""Cross-resource contract tests, parametrized over all six resources."""

import pytest
from jsonschema.validators import validator_for

from data import COUNTS, RESOURCES
from helpers import assert_status, get_json
from schemas import SCHEMAS

pytestmark = pytest.mark.contract


@pytest.mark.parametrize("resource", RESOURCES)
def test_list_returns_documented_number_of_items(fetch_list, resource):
    assert len(fetch_list(resource)) == COUNTS[resource]


@pytest.mark.parametrize("resource", RESOURCES)
def test_list_ids_are_unique(fetch_list, resource):
    ids = [item["id"] for item in fetch_list(resource)]
    assert len(ids) == len(set(ids))


@pytest.mark.schema
@pytest.mark.parametrize("resource", RESOURCES)
def test_list_items_match_schema(fetch_list, resource):
    # Build the validator once: validate() re-checks the schema on every call (5000 photos).
    schema = SCHEMAS[resource]
    validator = validator_for(schema)(schema)
    for item in fetch_list(resource):
        validator.validate(item)


@pytest.mark.schema
@pytest.mark.parametrize("resource", RESOURCES)
def test_get_by_id_returns_matching_item_that_matches_schema(api_client, resource):
    body = get_json(api_client.get(f"/{resource}/1"))
    schema = SCHEMAS[resource]
    validator_for(schema)(schema).validate(body)
    assert body["id"] == 1


@pytest.mark.parametrize("resource", RESOURCES)
def test_get_by_id_equals_item_in_list(api_client, fetch_list, resource):
    item = fetch_list(resource)[0]
    assert get_json(api_client.get(f"/{resource}/{item['id']}")) == item


@pytest.mark.negative
@pytest.mark.parametrize("resource", RESOURCES)
def test_get_nonexistent_id_returns_404(api_client, resource):
    assert_status(api_client.get(f"/{resource}/999999"), 404)


@pytest.mark.parametrize("resource", RESOURCES)
def test_responses_are_json(api_client, resource):
    resp = api_client.get(f"/{resource}/1")
    assert_status(resp, 200)
    assert resp.headers["Content-Type"].startswith("application/json")
