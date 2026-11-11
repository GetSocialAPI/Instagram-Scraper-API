# Instagram Scraper API

Get Instagram profiles, posts, stories, followers, comments, and more with 22
GetSocialAPI operations on Apify. Run this Actor with your Apify account.
No separate GetSocialAPI account or API key is required.

**No Instagram account or Instagram session cookies are required.**

## Input examples

Get a profile by username:

```json
{"operation": "profile", "target": "nike"}
```

Get multiple profiles by username:

```json
{"operation": "profile", "usernames": ["nike", "adidas"]}
```

Get a page of posts for a numeric Instagram user ID:

```json
{"operation": "posts", "target": "25025320", "count": 12}
```

## Pricing and output

Apify charges for each API response saved to the default Dataset. Each row
contains `operation`, `target`, and the raw API response in `data`. A single
profile uses one event. A page of 25 followers also uses one event for the whole
page. See the Pricing tab for the current rate.

## Operations

| Target | Operations |
| --- | --- |
| Username | `profile` |
| Instagram user ID | `profile_by_id`, `user_info`, `user_about`, `similar_users`, `posts`, `tagged_posts`, `stories`, `highlights`, `followers`, `following` |
| Highlight ID | `highlight_stories` |
| Media ID or shortcode | `media_info`, `media_likers`, `comments` |
| Search term | `search_users`, `search_reels`, `search_hashtags` |
| Hashtag | `hashtag_info`, `hashtag_posts` |
| Location ID | `location_info`, `location_posts` |

Use `count` with `search_users`, `posts`, `tagged_posts`, `followers`,
`following`, and `comments`. Use `query` to filter followers or following.

Each list call returns one page. For verified profiles, `followers` returns
a single page of up to approximately 50 followers and no continuation cursor.

For `posts`, `tagged_posts`, `followers`,
`following`, `hashtag_posts`, or `location_posts`, pass `data.next_max_id` as
`max_id` in the next run when the response includes a cursor. For `comments`,
pass `data.next_min_id` as `min_id` and use the default `sort_order` of
`recent`. See the [API reference](https://getsocialapi.com/docs/) for route
limits and response fields.
