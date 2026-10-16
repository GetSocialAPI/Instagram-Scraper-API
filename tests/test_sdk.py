import json
import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from getsocialapi import Client, InstagramAPI  # noqa: E402
from getsocialapi.exceptions import (  # noqa: E402
    APIKeyError,
    BadRequestError,
    InstagramError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
)
from getsocialapi.http import Transport  # noqa: E402


def fake_response(status, body=None, headers=None):
    r = MagicMock()
    r.status_code = status
    r.headers = headers or {}
    r.text = json.dumps(body) if body is not None else ""
    r.json = (lambda b=body: b) if body is not None else (lambda: (_ for _ in ()).throw(ValueError()))
    return r


def make_client(session):
    return Client(api_key="test_key", session=session, max_retries=0)


class TestClient(unittest.TestCase):
    def test_requires_key(self):
        with self.assertRaises(ValueError):
            Client(api_key=None)

    def test_health_no_auth_header(self):
        s = MagicMock()
        s.request.return_value = fake_response(200, {"ok": True, "state": "ready"})
        c = make_client(s)
        self.assertEqual(c.health(), {"ok": True, "state": "ready"})
        kwargs = s.request.call_args.kwargs
        self.assertEqual(kwargs["headers"], {})


class TestErrors(unittest.TestCase):
    def _transport(self, resp):
        t = Transport(api_key="k", max_retries=0)
        t.session = MagicMock()
        t.session.request.return_value = resp
        return t

    def test_401(self):
        with self.assertRaises(APIKeyError):
            self._transport(fake_response(401, {"error": "bad key"})).request("GET", "/x")

    def test_400_message_field(self):
        from getsocialapi.exceptions import BadRequestError, NotFoundError
        e = BadRequestError(body={"message": "Location does not exist.", "status": "fail"})
        self.assertEqual(str(e), "Location does not exist.")
        n = NotFoundError(body={"message": "Location does not exist.", "status": "fail"})
        self.assertEqual(str(n), "Location does not exist.")
        g = NotFoundError(body={"error": {"code": 404, "message": "Unknown endpoint"}})
        self.assertEqual(str(g), "Unknown endpoint")

    def test_400_field(self):
        with self.assertRaises(BadRequestError) as ctx:
            self._transport(fake_response(400, {"error": "invalid id", "field": "user_id"})).request("GET", "/x")
        self.assertEqual(ctx.exception.field, "user_id")

    def test_404_not_found(self):
        with self.assertRaises(NotFoundError):
            self._transport(fake_response(404, {"message": "user does not exist", "status": "fail"})).request("GET", "/x")

    def test_429_retry_after(self):
        with self.assertRaises(RateLimitError) as ctx:
            self._transport(fake_response(429, {}, {"Retry-After": "7"})).request("GET", "/x")
        self.assertEqual(ctx.exception.retry_after, 7)

    def test_503(self):
        with self.assertRaises(ServiceUnavailableError):
            self._transport(fake_response(503, {})).request("GET", "/x")

    def test_ig_error(self):
        with self.assertRaises(InstagramError):
            self._transport(fake_response(500, {"message": "oops", "status": "fail"})).request("GET", "/x")


class TestInstagramAPI(unittest.TestCase):
    def api(self):
        t = MagicMock()
        return InstagramAPI(t), t

    def check(self, method, args, expected_path, expected_params=None, kwargs=None):
        a, t = self.api()
        getattr(a, method)(*args, **(kwargs or {}))
        call = t.request.call_args
        self.assertEqual(call.args, ("GET", expected_path))
        if expected_params is not None:
            self.assertEqual(call.kwargs.get("params"), expected_params)

    def test_profile(self):
        self.check("profile", ("25025320",), "/profile/25025320")

    def test_user_info(self):
        self.check("user_info", (25025320,), "/ig/user/info/25025320")

    def test_hashtag_info_trims_hash(self):
        self.check("hashtag_info", ("#gymgirl",), "/ig/hashtag/info/gymgirl")

    def test_hashtag_posts_trims_hash(self):
        self.check("hashtag_posts", ("#gymgirl",), "/v2/hashtag/posts/gymgirl")
        self.check("hashtag_posts", ("##gym girl",), "/v2/hashtag/posts/gym%20girl")

    def test_username_info(self):
        self.check("user_by_username", ("instagram",), "/ig/user/username_info/instagram")

    def test_search_username(self):
        self.check("search_username", ("du",), "/search/username/du", {"count": 10})

    def test_user_medias(self):
        self.check("user_medias", (25025320,), "/ig/user/media/25025320", {"count": 12})

    def test_user_medias_max_id(self):
        self.check("user_medias", (25025320,), "/ig/user/media/25025320",
                   {"count": 50, "max_id": "CUR"}, {"count": 50, "max_id": "CUR"})

    def test_followers_default(self):
        self.check("followers", (25025320,), "/followers/25025320", {"count": 50})

    def test_followers_page_and_filter(self):
        self.check("followers", (25025320,), "/followers/25025320",
                   {"count": 25, "max_id": "CUR", "query": "an"},
                   {"count": 25, "max_id": "CUR", "query": "an"})

    def test_following_default(self):
        self.check("following", (25025320,), "/following/25025320", {"count": 25})

    def test_following_page_and_filter(self):
        self.check("following", (25025320,), "/following/25025320",
                   {"count": 25, "max_id": "CUR", "query": "bo"},
                   {"count": 25, "max_id": "CUR", "query": "bo"})

    def test_media_comments_default(self):
        self.check("media_comments", (3141085633626004499,),
                   "/ig/media/comments/3141085633626004499",
                   {"sort_order": "recent"})

    def test_media_comments_page(self):
        cur = '{"cached_comments_cursor":"123","bifilter_token":"abc+/=|"}'
        self.check("media_comments", (3141085633626004499,),
                   "/ig/media/comments/3141085633626004499",
                   {"count": 50, "sort_order": "recent", "min_id": cur},
                   {"count": 50, "min_id": cur})

    def test_media_comments_ranked(self):
        self.check("media_comments", (3141085633626004499,),
                   "/ig/media/comments/3141085633626004499",
                   {"sort_order": "ranked"}, {"sort_order": "ranked"})

    def test_media_comments_bad_sort_order(self):
        a, _ = self.api()
        with self.assertRaises(ValueError):
            a.media_comments(3141085633626004499, sort_order="top")

    def test_media_comments_bad_count(self):
        a, _ = self.api()
        with self.assertRaises(ValueError):
            a.media_comments(3141085633626004499, count=51)

    def test_hashtag_posts_default(self):
        self.check("hashtag_posts", ("gymgirl",), "/v2/hashtag/posts/gymgirl")

    def test_hashtag_posts_max_id(self):
        self.check("hashtag_posts", ("gymgirl",), "/v2/hashtag/posts/gymgirl",
                   {"max_id": "CUR"}, {"max_id": "CUR"})

    def test_location_media(self):
        self.check("location_media", (213069402,), "/ig/location/media/213069402")

    def test_location_media_max_id(self):
        self.check("location_media", (213069402,), "/ig/location/media/213069402",
                   {"max_id": "NEXT"}, {"max_id": "NEXT"})

    def test_search_clips(self):
        self.check("search_clips", ("hello world",), "/ig/media/search_clips/hello%20world")

    def test_hashtag_search_no_count(self):
        self.check("hashtag_search", ("gym girl",), "/ig/hashtag/search/gym%20girl")

    def test_highlight_stories_trims_prefix(self):
        self.check("highlight_stories", ("highlight:18223279177302854",),
                   "/ig/highlight/stories/18223279177302854")
        self.check("highlight_stories", ("18223279177302854",),
                   "/ig/highlight/stories/18223279177302854")

    def test_validations(self):
        a, _ = self.api()
        for fn, bad in [
            (a.user_info, "12x"),
            (a.user_by_username, ""),
            (a.user_medias, 0),
        ]:
            with self.assertRaises(ValueError):
                fn(bad) if fn not in (a.user_medias,) else fn(1, count=0)
        with self.assertRaises(ValueError):
            a.search_clips("")


if __name__ == "__main__":
    unittest.main(verbosity=2)
