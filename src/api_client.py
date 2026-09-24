import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com")
DEFAULT_TIMEOUT = float(os.getenv("API_TIMEOUT", "10"))

# Retry only failures where no response came back (DNS, refused or dropped
# connections). Status codes are never retried, so tests still see the real
# 4xx/5xx the API returns.
RETRY_POLICY = Retry(
    total=3,
    connect=3,
    read=0,
    status=0,
    other=0,
    backoff_factor=0.5,
    allowed_methods=None,
    raise_on_status=False,
)


class ApiClient:
    """Thin wrapper around requests.Session for the JSONPlaceholder API."""

    def __init__(self, base_url: str = BASE_URL, timeout: float = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=RETRY_POLICY)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}{path}", **kwargs)

    def get(self, path: str, **kwargs) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def head(self, path: str, **kwargs) -> requests.Response:
        return self._request("HEAD", path, **kwargs)

    def options(self, path: str, **kwargs) -> requests.Response:
        return self._request("OPTIONS", path, **kwargs)

    def post(self, path: str, json: dict | None = None, **kwargs) -> requests.Response:
        return self._request("POST", path, json=json, **kwargs)

    def put(self, path: str, json: dict | None = None, **kwargs) -> requests.Response:
        return self._request("PUT", path, json=json, **kwargs)

    def patch(self, path: str, json: dict | None = None, **kwargs) -> requests.Response:
        return self._request("PATCH", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self._request("DELETE", path, **kwargs)

    def close(self) -> None:
        self.session.close()
