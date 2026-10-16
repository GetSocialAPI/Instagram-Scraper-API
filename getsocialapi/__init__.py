from .client import Client
from .exceptions import (
    APIKeyError,
    BadRequestError,
    GetSocialAPIError,
    InstagramError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
)
from .instagram import InstagramAPI

__version__ = "0.1.0"

__all__ = [
    "Client",
    "InstagramAPI",
    "GetSocialAPIError",
    "BadRequestError",
    "APIKeyError",
    "NotFoundError",
    "RateLimitError",
    "ServiceUnavailableError",
    "InstagramError",
]
