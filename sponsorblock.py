import hashlib

import aiohttp

from state import sponsorblock_cache

CATEGORY_NAMES = {
    "music_offtopic": "non-music",
    "sponsor": "sponsored",
}


async def get_segments(video_id: str):
    if video_id in sponsorblock_cache:
        return sponsorblock_cache[video_id]

    hashPrefix = hashlib.sha256(video_id.encode()).hexdigest()[:4]
    session = aiohttp.ClientSession()
    response = await session.get(
        f"https://sponsor.ajay.app/api/skipSegments/{hashPrefix}",
        params={"categories": '["sponsor", "music_offtopic"]'},
    )
    if response.status == 200 and (
        results := list(
            filter(lambda v: video_id == v["videoID"], await response.json())
        )
    ):
        sponsorblock_cache[video_id] = results[0]
        return results[0]
