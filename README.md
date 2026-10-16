# getsocialapi-python

[![tests](https://github.com/GetSocialAPI/Instagram-Scraper-API/actions/workflows/tests.yml/badge.svg)](https://github.com/GetSocialAPI/Instagram-Scraper-API/actions/workflows/tests.yml)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org)

Python client for the **[GetSocialAPI](https://getsocialapi.com/)** Instagram Scraper API.

- **No cookies required** — you never provide Instagram session cookies
- **No accounts needed** — zero ban risk for your own profiles
- Raw Instagram JSON responses, REST endpoints — no transformations
- Automatic retries with `Retry-After`, typed exceptions

## Installation

```bash
pip install git+https://github.com/GetSocialAPI/Instagram-Scraper-API.git
```

## Quickstart

```python
from getsocialapi import Client

# Get your API key at https://getsocialapi.com/dashboard/
client = Client(api_key="gsa_live_...")  # or set GETSOCIALAPI_API_KEY

# Profile by numeric id (or user_by_username for usernames)
user = client.instagram.user_info(25025320)
print(user["user"]["follower_count"])

# Posts (grid)
medias = client.instagram.user_medias(25025320, count=12)

# Followers / following — paginated on unverified accounts: pass `next_max_id`
# back as `max_id`. Verified accounts (blue checkmark) expose ~50 followers max.
page = client.instagram.followers(43586162288, count=25)
page = client.instagram.followers(43586162288, max_id=page["next_max_id"])
```

Base URL: `https://api.getsocialapi.com/v1` — authenticate with the API key
from your [dashboard](https://getsocialapi.com/dashboard/).

## Client

```python
Client(api_key=None, base_url="https://api.getsocialapi.com/v1", timeout=30, max_retries=3)
```

| Parameter | Default | Description |
| --- | --- | --- |
| `api_key` | env `GETSOCIALAPI_API_KEY` | your API key |
| `base_url` | API endpoint | override only for testing |
| `timeout` | `30` | per-request timeout, seconds |
| `max_retries` | `3` | retries on 429/503/5xx and network errors |

## Methods

| Method | Route | Description |
| --- | --- | --- |
| `profile(user_id)` | `/profile/<id>` | profile by numeric id |
| `user_info(user_id)` | `/ig/user/info/<id>` | profile by numeric id |
| `user_by_username(username)` | `/ig/user/username_info/<username>` | profile by username |
| `search_username(query, count=10)` | `/search/username/<q>` | search users, resolve username → pk |
| `similar_users(user_id)` | `/ig/user/similar/<id>` | suggested accounts |
| `user_medias(user_id, count=12, max_id=None)` | `/ig/user/media/<id>` | profile grid posts |
| `user_tags(user_id, count=12, max_id=None)` | `/ig/user/tags/<id>` | posts with the user tagged |
| `user_stories(user_id)` | `/ig/user/stories/<id>` | active stories |
| `user_highlights(user_id)` | `/ig/user/highlights/<id>` | highlights tray |
| `highlight_stories(highlight_id)` | `/ig/highlight/stories/<id>` | media of a highlight |
| `followers(user_id, count=50, max_id=None, query=None)` | `/followers/<id>` | followers list |
| `following(user_id, count=25, max_id=None, query=None)` | `/following/<id>` | following list |
| `media_info(pk)` | `/ig/media/info/<pk>` | full media card |
| `media_likers(pk)` | `/ig/media/likers/<pk>` | users who liked |
| `media_comments(pk)` | `/ig/media/comments/<pk>` | media comments |
| `search_clips(keyword)` | `/ig/media/search_clips/<kw>` | search reels by keyword |
| `hashtag_info(tag)` | `/ig/hashtag/info/<tag>` | hashtag card |
| `hashtag_search(query)` | `/ig/hashtag/search/<q>` | search hashtags |
| `hashtag_posts(tag, max_id=None)` | `/v2/hashtag/posts/<tag>` | posts by hashtag |
| `location_info(pk)` | `/ig/location/info/<pk>` | location card |
| `location_media(pk, max_id=None)` | `/ig/location/media/<pk>` | media by location |

Every method returns the raw JSON of the API route as received — nothing is
unwrapped, filtered or renamed. Where the API supports pagination (`followers`*, `following`, `user_medias`,
`user_tags`, `hashtag_posts`, `location_media`), pass the cursor from the
previous response (`next_max_id`) as `max_id`.
*`followers` works on unverified accounts (nearly the full list, plus the
`query` filter); verified accounts (blue checkmark) expose no more than ~50
followers — one page, no cursor, `query` ignored. For lists without cursors (`media_comments`, `search_clips`,
`hashtag_search`) each call simply returns the service page.

Full request/response reference with live examples:
[docs.getsocialapi → API Reference](https://getsocialapi.com/docs/api/instagram/user/get_info_by_id/)
(see the Documentation section on [getsocialapi.com](https://getsocialapi.com/)).

## Errors

| Exception | HTTP | Notes |
| --- | --- | --- |
| `GetSocialAPIError` | — | base class; also network errors |
| `APIKeyError` | 401 | invalid or missing key |
| `BadRequestError` | 400 | `.field` points to the bad parameter |
| `NotFoundError` | 404 | object does not exist — never retried |
| `RateLimitError` | 429 | `.retry_after` seconds |
| `ServiceUnavailableError` | 503 | no live accounts, `.retry_after` |
| `InstagramError` | any | upstream Instagram error, `.status` |

```python
from getsocialapi import NotFoundError, RateLimitError
import time

try:
    client.instagram.user_info(25025320)
except NotFoundError:
    ...  # object does not exist
except RateLimitError as e:
    time.sleep(e.retry_after)
```

Only successful responses (HTTP `200` and `404`) count against your quota.
Rate limits and plans: [pricing](https://getsocialapi.com/#pricing).

## Support

- Email: [hello@getsocialapi.com](mailto:hello@getsocialapi.com)
- Website: [getsocialapi.com](https://getsocialapi.com/)
- Documentation: [getsocialapi.com/docs](https://getsocialapi.com/docs/)
- Status: [getsocialapi.com/status](https://getsocialapi.com/status/)

## License

MIT
