class GetSocialAPIError(Exception):
    """Base error for all GetSocialAPI SDK failures."""

    def __init__(self, message, response=None, body=None):
        super().__init__(message)
        self.response = response
        self.body = body if body is not None else {}


def _reason(body, fallback):
    """Extract a human-readable reason: {"error": "..."} | {"error": {"message"}} | {"message": ..."}."""
    err = body.get("error")
    if isinstance(err, dict):
        err = err.get("message")
    if isinstance(err, str) and err:
        return err
    msg = body.get("message")
    if isinstance(msg, str) and msg:
        return msg
    return fallback


class BadRequestError(GetSocialAPIError):
    """400 — invalid parameters (body: {"error", "field"})."""

    def __init__(self, response=None, body=None):
        body = body or {}
        field = body.get("field")
        msg = _reason(body, "Bad request")
        if field:
            msg = f"{msg} (field: {field})"
        super().__init__(msg, response, body)
        self.field = field


class UnauthorizedError(GetSocialAPIError):
    """401 — invalid or missing API key."""

    def __init__(self, response=None, body=None):
        super().__init__("Invalid API key", response, body)


class NotFoundError(GetSocialAPIError):
    """404 — target object does not exist. Do not retry."""

    def __init__(self, response=None, body=None):
        body = body or {}
        msg = _reason(body, "Not found")
        super().__init__(msg, response, body)


class RateLimitError(GetSocialAPIError):
    """429 — key rate limit exceeded. Honors Retry-After."""

    def __init__(self, response=None, body=None, retry_after=1):
        super().__init__(f"Rate limit exceeded, retry after {retry_after}s", response, body)
        self.retry_after = retry_after


class ServiceUnavailableError(GetSocialAPIError):
    """503 — no live accounts or the service is stopped."""

    def __init__(self, response=None, body=None, retry_after=None):
        msg = "Service unavailable"
        if retry_after:
            msg += f", retry after {retry_after}s"
        super().__init__(msg, response, body)
        self.retry_after = retry_after


class InstagramError(GetSocialAPIError):
    """Non-404 error returned by the Instagram private API (raw mode)."""

    def __init__(self, status, message, response=None, body=None):
        super().__init__(f"Instagram API error {status}: {message}", response, body)
        self.status = status


# Convenience alias
APIKeyError = UnauthorizedError
