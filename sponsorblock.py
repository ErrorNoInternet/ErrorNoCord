import hashlib

import requests

from state import sponsorblock_cache


def get_segments(videoId: str):
    if videoId in sponsorblock_cache:
        return sponsorblock_cache[videoId]

    hashPrefix = hashlib.sha256(videoId.encode()).hexdigest()[:4]
    response = requests.get(
        f'https://sponsor.ajay.app/api/skipSegments/{hashPrefix}?categories=["music_offtopic"]'
    )
    print(response.text)
    if response.status_code == 200 and (
        results := list(filter(lambda v: videoId == v["videoID"], response.json()))
    ):
        sponsorblock_cache[videoId] = results[0]
        return results[0]
