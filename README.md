# SDET Technical Assessment – API Test Automation

Automated API test suite for the [JSONPlaceholder](https://jsonplaceholder.typicode.com) REST API, built with Python, pytest, `requests` and `jsonschema`.

## Overview

The suite exercises all six JSONPlaceholder resources (`/posts`, `/comments`, `/albums`, `/photos`, `/todos`, `/users`).

- `src/api_client.py`: thin `requests.Session` wrapper (`get/head/options/post/put/patch/delete`). The base URL and timeout come from environment variables, and connection failures are retried (HTTP error statuses never are, so tests always see the real response).
- `tests/conftest.py`: session-scoped `api_client` fixture (closed at the end of the run) and a `fetch_list` fixture that downloads each resource list once per run.
- `tests/data.py`: the static dataset (resource counts) and write payloads; expected new ids are derived from the counts.
- `tests/helpers.py`: `assert_status`, `get_json` and `get_non_empty_list`. Failures print the method, URL, status and response body, and list checks can't pass on an empty response.
- `tests/schemas.py`: strict JSON schemas for all six resources (no missing or unexpected fields), including the nested user `address`, `geo` and `company` objects.
- `tests/test_contract.py`: one parametrized set of checks (count, unique ids, schema, get-by-id, 404, JSON header) run against all six resources.
- `tests/test_crud.py`: POST / PUT / PATCH / DELETE and related negative cases, parametrized across all six resources.
- `tests/test_query.py`: server-side query features: pagination, `_start`/`_end`, sorting, range operators, full-text search, `_embed` and `_expand`.
- `tests/test_posts.py`: `/posts` specifics: author filter, nested comments, referential integrity, malformed ids.
- `tests/test_routes.py`: nested routes (and their equivalence to filters), unknown routes, nonexistent parents, HEAD and CORS preflight.
- `tests/test_users.py`: nested-object content and data integrity (unique emails and usernames, valid coordinates).
- `tests/test_filters.py`: single- and multi-parameter query filtering, compared against the full list.
- `tests/test_smoke.py`: reachability and response-time budget.

### Assumptions

- JSONPlaceholder is a fake API: writes (POST/PUT/PATCH/DELETE) are echoed but **never persisted**. Tests therefore assert only on the response of the call that made the change and never depend on ordering or on earlier writes.
- The API does not validate input. Tests assert the **observed** behaviour and flag surprises in comments rather than what a strict API should do:
  - `POST /posts` with `{}` returns `201` with only a generated `id`.
  - Malformed or unknown ids (`abc`, `-1`, `0`, `999999`) return `404`, not `400`.
  - `PUT` on a nonexistent id (e.g. `/posts/999999`) returns `500`, not `404`.
  - `PATCH` returns the full resource with the patched field merged in.
- The dataset is static (100 posts, 500 comments, 100 albums, 5000 photos, 200 todos, 10 users), so counts are asserted.
- Tests need internet access to `jsonplaceholder.typicode.com`.

### Scope of testing completed

- **Contract (all 6 resources):** list is 200 with the documented item count and unique ids; every item matches its schema; `GET /{id}` matches the schema and equals the item in the list; unknown id is 404; `Content-Type` is JSON.
- **Write operations (all 6 resources):** POST (201, echoed fields, next generated id), PUT, PATCH (only the patched field changes), DELETE (200, `{}`), writes not persisted, empty POST body, PUT on a nonexistent id.
- **Query features:** `_page`/`_limit` (including `X-Total-Count` and `Link` headers, and a page past the end), `_start`/`_end`, `_sort`/`_order`, `_gte`/`_lte`, `q` search, `_embed`, `_expand`. Results are compared with the full list, not just their shape.
- **Posts:** `userId` filter (match and no match), `/posts/1/comments`, every post has an existing user and every comment an existing post, malformed ids.
- **Routes:** all five nested routes (`/posts/{id}/comments`, `/albums/{id}/photos`, `/users/{id}/albums|todos|posts`) return the same result as the equivalent filter; unknown routes (404); nested route of a nonexistent parent (empty list); HEAD; CORS preflight and origin header.
- **Users:** nested objects populated, unique emails and usernames, valid latitude/longitude.
- **Filters:** single- and multi-parameter filters (`postId`, `userId`, `albumId`, `completed`) return exactly the matching items.
- **Smoke:** API reachable and responds within the time budget.

## Execution Instructions

### 1. Install dependencies

Requires Python 3.10+.

```bash
python -m venv .venv --prompt sdet_Assessment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Build

Not applicable: this is a pure-Python project with no compile or packaging step. Installing the dependencies is all the setup needed.

### 3. Run the test suite

```bash
pytest
```

Run a subset with markers, e.g. `pytest -m smoke`, `pytest -m negative`, `pytest -m schema`, `pytest -m contract`.

Configuration (all optional):

| Variable | Default | Purpose |
|---|---|---|
| `API_BASE_URL` | `https://jsonplaceholder.typicode.com` | Run the suite against another environment, e.g. a local json-server |
| `API_TIMEOUT` | `10` | Request timeout in seconds |
| `API_MAX_RESPONSE_SECONDS` | `3` | Response-time budget for the smoke tests |

Lint and format checks (also run in CI):

```bash
ruff check .
ruff format --check .
```

### 4. View test results

```bash
pytest --html=report.html --self-contained-html
```

Open `report.html` in a browser. On GitHub Actions the same report is published as a downloadable workflow artifact (`pytest-report-py<version>`) on every push, PR and nightly run (see the **Actions** tab).

## Coverage Summary

| Area | Coverage |
|---|---|
| Routes | `GET` list and by id, plus `POST`, `PUT`, `PATCH`, `DELETE`, on all 6 resources; all 5 nested routes; `HEAD` and `OPTIONS` |
| Validation types | Status codes, strict JSON schema (all 6 resources), response headers (`Content-Type`, `X-Total-Count`, `Link`, CORS), data values, list sizes, uniqueness, referential integrity, filtering, pagination, sorting, search, response time |
| Negative cases | Nonexistent and malformed ids, unknown routes, empty POST body, PUT on a nonexistent id, non-persistence of writes, filter with no match, page past the end |

**Intentionally omitted (time box / not applicable):**

- Property-based or fuzz testing, load and concurrency testing.
- Auth testing (the API has no auth).

## CI/CD

GitHub Actions ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs on every push and pull request to `main`, nightly (to catch upstream API changes) and on demand:

- **lint:** `ruff check` and `ruff format --check`.
- **test:** on Python 3.10 and 3.12, the smoke tests run first so an API outage fails fast, then the full suite, which publishes an HTML report as a build artifact.
