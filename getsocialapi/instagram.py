from urllib.parse import quote


def _quote(value):
    return quote(str(value), safe="")


def _digits(value, name, max_len=20):
    s = str(value)
    if not s.isdigit() or not 1 <= len(s) <= max_len:
        raise ValueError(f"{name} must be 1-{max_len} digits, got: {value!r}")
    return s


def _length(value, name, lo, hi):
    s = str(value)
    if not lo <= len(s) <= hi:
        raise ValueError(f"{name} must be {lo}-{hi} characters, got: {value!r}")
    return s


def _tag(value):
    return _quote(_length(str(value).lstrip("#"), "tag", 1, 64))


def _count(value, lo=1, hi=50, default=None):
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
        raise ValueError(f"count must be an integer {lo}-{hi}, got: {value!r}")
    return value


class InstagramAPI:
    """Instagram endpoints of GetSocialAPI.

    Methods map 1:1 to API routes and return the raw JSON responses as received.
    """

    def __init__(self, transport):
        self._t = transport

    # ---------- Profile ----------

    def user_info(self, user_id):
        """GET /ig/user/info/{user_id} — profile by numeric id."""
        return self._t.request("GET", f"/ig/user/info/{_digits(user_id, 'user_id')}")

    def user_by_username(self, username):
        """GET /ig/user/username_info/{username} — profile by username."""
        return self._t.request("GET", f"/ig/user/username_info/{_length(username, 'username', 1, 64)}")

    def profile(self, user_id):
        """GET /profile/{user_id} — profile by numeric id."""
        return self._t.request("GET", f"/profile/{_digits(user_id, 'user_id')}")

    def search_username(self, query, count=10):
        """GET /search/username/{query} — search users.

        `count` is forwarded to the service, but the response may include
        one extra exact-match entry beyond it.
        """
        return self._t.request("GET", f"/search/username/{_quote(query)}",
                               params={"count": _count(count, default=10)})

    def similar_users(self, user_id):
        """GET /ig/user/similar/{user_id} — suggested accounts."""
        return self._t.request("GET", f"/ig/user/similar/{_digits(user_id, 'user_id')}")

    # ---------- User content ----------

    def user_medias(self, user_id, count=12, max_id=None):
        """GET /ig/user/media/{user_id} — profile grid posts."""
        return self._t.request("GET", f"/ig/user/media/{_digits(user_id, 'user_id')}",
                               params=_page(count, max_id, default=12))

    def user_tags(self, user_id, count=12, max_id=None):
        """GET /ig/user/tags/{user_id} — posts where the user is tagged."""
        return self._t.request("GET", f"/ig/user/tags/{_digits(user_id, 'user_id')}",
                               params=_page(count, max_id, default=12))

    def user_stories(self, user_id):
        """GET /ig/user/stories/{user_id} — active stories."""
        return self._t.request("GET", f"/ig/user/stories/{_digits(user_id, 'user_id')}")

    def user_highlights(self, user_id):
        """GET /ig/user/highlights/{user_id} — highlights tray."""
        return self._t.request("GET", f"/ig/user/highlights/{_digits(user_id, 'user_id')}")

    def highlight_stories(self, highlight_id):
        """GET /ig/highlight/stories/{highlight_id} — media of a highlight.

        Accepts the tray id as is — the leading `highlight:` prefix
        (as returned by `user_highlights`) is trimmed automatically.
        """
        hid = str(highlight_id)
        if hid.startswith("highlight:"):
            hid = hid[len("highlight:"):]
        return self._t.request("GET", f"/ig/highlight/stories/{_quote(_length(hid, 'highlight_id', 1, 64))}")

    # ---------- Followers / following ----------

    def followers(self, user_id, count=50, max_id=None, query=None):
        """GET /followers/{user_id} — followers list.

        On regular accounts `count` and the `next_max_id` cursor work and
        `query` searches inside the list (pages of 25). For profiles with
        millions of followers Instagram hard-limits the list to a single
        native page (~43-50, `should_limit_list_of_followers`) without a
        cursor — enumerate the hidden part with `query`.
        """
        params = _page(count, max_id, default=50)
        if query is not None:
            params["query"] = query
        return self._t.request("GET", f"/followers/{_digits(user_id, 'user_id')}",
                               params=params)

    def following(self, user_id, count=25, max_id=None, query=None):
        """GET /following/{user_id} — following list.

        Page size: the service returns the default 25 accounts per page and
        at most 25 (values above 50 are rejected). The response carries
        `next_max_id` — pass it as `max_id` for the next page. `query`
        filters the list by name.
        """
        params = _page(count, max_id, default=25, hi=50)
        if query is not None:
            params["query"] = query
        return self._t.request("GET", f"/following/{_digits(user_id, 'user_id')}",
                               params=params)

    # ---------- Media ----------

    def media_info(self, pk):
        """GET /ig/media/info/{pk} — full media card."""
        return self._t.request("GET", f"/ig/media/info/{_digits(pk, 'pk')}")

    def media_likers(self, pk):
        """GET /ig/media/likers/{pk} — users who liked the media."""
        return self._t.request("GET", f"/ig/media/likers/{_digits(pk, 'pk')}")

    def media_comments(self, pk):
        """GET /ig/media/comments/{pk} — media comments.

        Instagram returns only the preview block of recent comments
        (~8-15, `can_view_more_preview_comments=false`) without a functional
        cursor, regardless of `comment_count` — the full list is closed
        server-side.
        """
        return self._t.request("GET", f"/ig/media/comments/{_digits(pk, 'pk')}")

    def search_clips(self, keyword):
        """GET /ig/media/search_clips/{keyword} — search reels by keyword.

        The service returns its native page (~12 clips); a page-size
        parameter is not supported by the API for this route.
        """
        kw = _length(keyword, "keyword", 1, 100)
        return self._t.request("GET", f"/ig/media/search_clips/{_quote(kw)}")

    # ---------- Hashtags ----------

    def hashtag_info(self, tag):
        """GET /ig/hashtag/info/{tag} — hashtag card. A leading # is trimmed."""
        return self._t.request("GET", f"/ig/hashtag/info/{_tag(tag)}")

    def hashtag_search(self, query):
        """GET /ig/hashtag/search/{query} — search hashtags.

        Returns the full first page of tag matches; a page-size
        parameter is not supported by the API for this route.
        """
        return self._t.request("GET", f"/ig/hashtag/search/{_quote(query)}")

    def hashtag_posts(self, tag, max_id=None):
        """GET /v2/hashtag/posts/{tag} — posts by hashtag. A leading # is trimmed.

        The service returns its native page (~15-18 posts) plus `next_max_id`
        for pagination via `max_id`; a page-size parameter is not supported.
        """
        params = {"max_id": max_id} if max_id is not None else None
        return self._t.request("GET", f"/v2/hashtag/posts/{_tag(tag)}",
                               params=params)

    # ---------- Locations ----------

    def location_info(self, pk):
        """GET /ig/location/info/{pk} — location card."""
        return self._t.request("GET", f"/ig/location/info/{_digits(pk, 'pk')}")

    def location_media(self, pk, max_id=None):
        """GET /ig/location/media/{pk} — media by location.

        The service returns its native page; pass `next_max_id` from a
        previous response as `max_id` to request the next page. The
        response also carries `next_page` — a page counter, not a cursor.
        """
        params = {"max_id": max_id} if max_id is not None else None
        return self._t.request("GET", f"/ig/location/media/{_digits(pk, 'pk')}",
                               params=params)


def _page(count, max_id, default=12, hi=50):
    params = {"count": _count(count, default=default, hi=hi)}
    if max_id is not None:
        params["max_id"] = max_id
    return params
