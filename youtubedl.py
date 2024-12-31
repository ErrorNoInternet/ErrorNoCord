import asyncio
from typing import Any, Optional

import disnake
import yt_dlp

import constants
import utils

ytdl = yt_dlp.YoutubeDL(constants.YTDL_OPTIONS)


class YTDLSource(disnake.PCMVolumeTransformer):
    def __init__(
        self, source: disnake.AudioSource, *, data: dict[str, Any], volume: float = 0.5
    ):
        super().__init__(source, volume)
        self.title = data.get("title")
        self.original_url = data.get("original_url")
        self.duration = data.get("duration")

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
            data = data["entries"][0]

        return cls(
            disnake.FFmpegPCMAudio(
                data["url"] if stream else ytdl.prepare_filename(data),
                before_options="-vn -reconnect 1",
            ),
            data=data,
        )


class QueuedPlayer:
    def __init__(self):
        self.queue = []
        self.current = None

    def queue_pop(self):
        popped = self.queue[0]
        del self.queue[0]
        self.current = popped
        return popped

    def queue_add(self, item):
        self.queue.append(item)


class QueuedSong:
    def __init__(self, player, queuer):
        self.player = player
        self.queuer = queuer

    def format(self, with_queuer=False, hide_preview=False) -> str:
        return (
            f"[`{self.player.title}`]({'<' if hide_preview else ''}{self.player.original_url}{'>' if hide_preview else ''}) [{self.format_duration(self.player.duration)}]"
            + (f" (<@{self.queuer}>)" if with_queuer else "")
        )

    def format_duration(self, duration: int) -> str:
        segments = []
        hours, duration = divmod(duration, 3600)
        if hours > 0:
            segments.append(hours)
        minutes, duration = divmod(duration, 60)
        if minutes > 0:
            segments.append(minutes)
        if duration > 0:
            segments.append(duration)
        return f"{':'.join(str(s) for s in segments)}"


def __reload_module__():
    global ytdl
    ytdl = yt_dlp.YoutubeDL(constants.YTDL_OPTIONS)
