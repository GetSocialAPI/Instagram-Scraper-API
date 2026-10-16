import time

import requests

from .exceptions import (
    BadRequestError,
    GetSocialAPIError,
    InstagramError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnauthorizedError,
)

DEFAULT_BASE_URL = "https://api.getsocialapi.com/v1"

RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class Transport:
    """HTTP transport: auth, JSON parsing, retries with Retry-After."""

    def __init__(self, base_url=DEFAULT_BASE_URL, api_key=None, timeout=30,
                 max_retries=3, session=None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = session or requests.Session()

    def request(self, method, path, params=None, auth=True):
        url = f"{self.base_url}{path}"
        headers = {"X-API-Key": self.api_key} if auth else {}
        attempts = self.max_retries + 1
        last_exc = None
        for attempt in range(attempts):
            try:
                resp = self.session.request(
                    method, url, params=params, headers=headers, timeout=self.timeout,
                )
            except (requests.ConnectionError, requests.Timeout) as e:
                last_exc = e
                if attempt < attempts - 1:
                    time.sleep(min(2 ** attempt, 10))
                    continue
                raise GetSocialAPIError(f"Network error: {e}") from e

            if resp.status_code in RETRYABLE_STATUS and attempt < attempts - 1:
                time.sleep(self._retry_after(resp))
                continue
            return self._parse(resp)
        raise GetSocialAPIError("Request failed after retries")  # pragma: no cover

    @staticmethod
    def _retry_after(resp):
        try:
            return min(max(int(float(resp.headers.get("Retry-After", 1))), 0), 30)
        except (TypeError, ValueError):
            return 1

    def _parse(self, resp):
        try:
            body = resp.json()
        except ValueError:
            body = {"raw": resp.text}

        if resp.status_code == 401:
            raise UnauthorizedError(resp, body)
        if resp.status_code == 400:
            raise BadRequestError(resp, body)
        if resp.status_code == 404:
            raise NotFoundError(resp, body)
        if resp.status_code == 429:
            raise RateLimitError(resp, body, retry_after=self._retry_after(resp))
        if resp.status_code == 503:
            raise ServiceUnavailableError(resp, body, retry_after=self._retry_after(resp))
        if resp.status_code >= 400:
            # Instagram errors in raw mode: {"message": "...", "status": "fail"}
            if isinstance(body, dict) and body.get("status") == "fail":
                raise InstagramError(resp.status_code, body.get("message", "unknown"), resp, body)
            raise GetSocialAPIError(f"HTTP {resp.status_code}: {body}", resp, body)
        return body
