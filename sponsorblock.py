import hashlib

import aiohttp

from state import sponsorblock_cache

CATEGORY_NAMES = {
    "music_offtopic": "non-music",
    "sponsor": "sponsored",
}


async def get_segments(videoId: str):
    if videoId in sponsorblock_cache:
        return sponsorblock_cache[videoId]

    hashPrefix = hashlib.sha256(videoId.encode()).hexdigest()[:4]
    session = aiohttp.ClientSession()
    response = await session.get(
        f"https://sponsor.ajay.app/api/skipSegments/{hashPrefix}",
        params={"categories": '["sponsor", "music_offtopic"]'},
    )
    if response.status == 200 and (
        results := list(
            filter(lambda v: videoId == v["videoID"], await response.json())
        )
    ):
        sponsorblock_cache[videoId] = results[0]
        return results[0]
