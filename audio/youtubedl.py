import asyncio
from typing import Any, Optional

import disnake
import yt_dlp

from constants import YTDL_OPTIONS

from .discord import PCMVolumeTransformer, TrackedAudioSource

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


class YTDLSource(PCMVolumeTransformer):
    def __init__(
        self, source: TrackedAudioSource, *, data: dict[str, Any], volume: float = 0.5
    ):
        super().__init__(source, volume)

        self.description = data.get("description")
        self.duration = data.get("duration")
        self.id = data.get("id")
        self.like_count = data.get("like_count")
        self.original_url = data.get("original_url")
        self.thumbnail_url = data.get("thumbnail")
        self.timestamp = data.get("timestamp")
        self.title = data.get("title")
        self.uploader = data.get("uploader")
        self.uploader_url = data.get("uploader_url")
        self.view_count = data.get("view_count")

    @classmethod
    async def from_url(
        cls,
        url,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        stream: bool = False,
    ):
        loop = loop or asyncio.get_event_loop()
        data: Any = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            if not data["entries"]:
                raise Exception("no results found!")
            data = data["entries"][0]

        return cls(
            TrackedAudioSource(
                disnake.FFmpegPCMAudio(
                    data["url"] if stream else ytdl.prepare_filename(data),
                    before_options="-vn -reconnect 1",
                )
            ),
            data=data,
        )

    def __repr__(self):
        return f"<YTDLSource title={self.title} original_url=<{self.original_url}> duration={self.duration}>"

    def __str__(self):
        return self.__repr__()


def __reload_module__():
    global ytdl
    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)
