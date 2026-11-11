import asyncio
import re

from apify import Actor
from getsocialapi_instagram import Client, GetSocialAPIError


# Only explicitly listed SDK methods can be invoked by Actor input.
OPERATIONS = {
    "profile": ("user_by_username", ()),
    "profile_by_id": ("profile", ()),
    "user_info": ("user_info", ()),
    "user_about": ("user_about", ()),
    "search_users": ("search_username", ("count",)),
    "similar_users": ("similar_users", ()),
    "posts": ("user_medias", ("count", "max_id")),
    "tagged_posts": ("user_tags", ("count", "max_id")),
    "stories": ("user_stories", ()),
    "highlights": ("user_highlights", ()),
    "highlight_stories": ("highlight_stories", ()),
    "followers": ("followers", ("count", "max_id", "query")),
    "following": ("following", ("count", "max_id", "query")),
    "media_info": ("media_info", ()),
    "media_likers": ("media_likers", ()),
    "comments": ("media_comments", ("count", "sort_order", "min_id")),
    "search_reels": ("search_clips", ()),
    "hashtag_info": ("hashtag_info", ()),
    "search_hashtags": ("hashtag_search", ()),
    "hashtag_posts": ("hashtag_posts", ("max_id",)),
    "location_info": ("location_info", ()),
    "location_posts": ("location_media", ("max_id",)),
}

OPTIONS = ("count", "max_id", "min_id", "query", "sort_order")


def parse_input(actor_input):
    operation = actor_input.get("operation", "profile")
    if not isinstance(operation, str) or operation not in OPERATIONS:
        raise ValueError("Choose a supported operation from the Actor input form.")

    target = actor_input.get("target")
    usernames = actor_input.get("usernames")
    if usernames is not None:
        if operation != "profile" or target is not None:
            raise ValueError("Use usernames only for profile, with target omitted.")
        if not isinstance(usernames, list) or not usernames:
            raise ValueError("Provide usernames as a non-empty array of strings.")

    targets = usernames if usernames is not None else [target]
    if any(not isinstance(value, str) or not value.strip() for value in targets):
        raise ValueError("Provide a non-empty target or an array of usernames.")
    targets = [value.strip() for value in targets]

    if operation == "profile":
        targets = [value.removeprefix("@") for value in targets]
        if any(
            not re.fullmatch(r"[a-zA-Z0-9_.]{1,30}", value) or value in (".", "..")
            for value in targets
        ):
            raise ValueError("Provide Instagram usernames, such as nike.")

    method, accepted_options = OPERATIONS[operation]
    options = {name: actor_input[name] for name in OPTIONS if actor_input.get(name) is not None}
    unsupported = options.keys() - set(accepted_options)
    if unsupported:
        raise ValueError(f"Unsupported options for {operation}: {', '.join(sorted(unsupported))}")

    return operation, method, targets, options


async def main():
    async with Actor:
        operation, method, targets, options = parse_input(await Actor.get_input() or {})
        request = getattr(Client().instagram, method)

        for target in targets:
            try:
                data = await asyncio.to_thread(request, target, **options)
            except GetSocialAPIError as error:
                status = getattr(error.response, "status_code", None)
                detail = f"HTTP {status}" if status is not None else type(error).__name__
                raise RuntimeError(f"GetSocialAPI request failed for {operation}: {detail}") from None

            await Actor.push_data({"operation": operation, "target": target, "data": data})


if __name__ == "__main__":
    asyncio.run(main())
