import os

from .http import DEFAULT_BASE_URL, Transport
from .instagram import InstagramAPI


class Client:
    """GetSocialAPI client.

    Usage:
        from getsocialapi import Client
        client = Client(api_key="gsa_live_...")
        client.instagram.user_by_username("durov")
    """

    def __init__(self, api_key=None, base_url=DEFAULT_BASE_URL, timeout=30,
                 max_retries=3, session=None):
        api_key = api_key or os.environ.get("GETSOCIALAPI_API_KEY")
        if not api_key:
            raise ValueError(
                "api_key is required (pass api_key=... or set GETSOCIALAPI_API_KEY)"
            )
        self._transport = Transport(
            base_url=base_url, api_key=api_key, timeout=timeout,
            max_retries=max_retries, session=session,
        )
        self.instagram = InstagramAPI(self._transport)

    def health(self):
        """Upstream liveness probe: {"ok": true, "state": "ready"}."""
        return self._transport.request("GET", "/health", auth=False)
