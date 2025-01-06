import asyncio
import collections
from dataclasses import dataclass
from typing import Any, Optional

import constants
import disnake
import yt_dlp

ytdl = yt_dlp.YoutubeDL(constants.YTDL_OPTIONS)


class TrackedAudioSource(disnake.AudioSource):
    def __init__(self, source):
        self._source = source
        self.count = 0

    def read(self) -> bytes:
        data = self._source.read()
        if data:
            self.count += 1
        return data

    @property
    def progress(self) -> float:
        return self.count * 0.02


class YTDLSource(disnake.PCMVolumeTransformer):
    def __init__(
        self, source: TrackedAudioSource, *, data: dict[str, Any], volume: float = 0.5
    ):
        super().__init__(source, volume)

        self.description = data.get("description")
        self.duration = data.get("duration")
        self.original_url = data.get("original_url")
        self.thumbnail_url = data.get("thumbnail")
        self.title = data.get("title")
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


@dataclass
class QueuedSong:
    player: YTDLSource
    trigger_message: disnake.Message

    def format(self, show_queuer=False, hide_preview=False, multiline=False) -> str:
        if multiline:
            return (
                f"[`{self.player.title}`]({'<' if hide_preview else ''}{self.player.original_url}{'>' if hide_preview else ''})\n**duration:** {format_duration(self.player.duration) if self.player.duration else '[live]'}"
                + (
                    f", **queued by:** <@{self.trigger_message.author.id}>"
                    if show_queuer
                    else ""
                )
            )
        else:
            return (
                f"[`{self.player.title}`]({'<' if hide_preview else ''}{self.player.original_url}{'>' if hide_preview else ''}) **[{format_duration(self.player.duration) if self.player.duration else 'live'}]**"
                + (f" (<@{self.trigger_message.author.id}>)" if show_queuer else "")
            )

    def __str__(self):
        return self.__repr__()


@dataclass
class QueuedPlayer:
    queue = collections.deque()
    current: Optional[QueuedSong] = None

    def queue_pop(self):
        popped = self.queue.popleft()
        self.current = popped
        return popped

    def queue_add(self, item):
        self.queue.append(item)

    def queue_add_front(self, item):
        self.queue.appendleft(item)

    def __str__(self):
        return self.__repr__()


def format_duration(duration: int) -> str:
    hours, duration = divmod(duration, 3600)
    minutes, duration = divmod(duration, 60)
    segments = [hours, minutes, duration]
    if len(segments) == 3 and segments[0] == 0:
        del segments[0]
    return f"{':'.join(f'{s:0>2}' for s in segments)}"


def __reload_module__():
    global ytdl
    ytdl = yt_dlp.YoutubeDL(constants.YTDL_OPTIONS)
