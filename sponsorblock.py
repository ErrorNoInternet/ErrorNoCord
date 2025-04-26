import hashlib
import json

import aiohttp

from state import sponsorblock_cache

categories = json.dumps(
    [
        "interaction",
        "intro",
        "music_offtopic",
        "outro",
        "preview",
        "selfpromo",
        "sponsor",
    ],
)


async def get_segments(video_id: str):
    if video_id in sponsorblock_cache:
        return sponsorblock_cache[video_id]

    hash_prefix = hashlib.sha256(video_id.encode()).hexdigest()[:4]
    session = aiohttp.ClientSession()
    response = await session.get(
        f"https://sponsor.ajay.app/api/skipSegments/{hash_prefix}",
        params={"categories": categories},
    )
    if response.status == 200 and (
        results := list(
            filter(lambda v: video_id == v["videoID"], await response.json()),
        )
    ):
        sponsorblock_cache[video_id] = results[0]
        return results[0]
