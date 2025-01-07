import asyncio
import collections
from dataclasses import dataclass
from typing import Any, Optional

import disnake
import yt_dlp

import constants

ytdl = yt_dlp.YoutubeDL(constants.YTDL_OPTIONS)


class CustomAudioSource(disnake.AudioSource):
    def __init__(self, source):
        self._source = source
        self.read_count = 0

    def read(self) -> bytes:
        data = self._source.read()
        if data:
            self.read_count += 1
        return data

    def fast_forward(self, seconds: int):
        for _ in range(int(seconds / 0.02)):
            self.read()

    @property
    def progress(self) -> float:
        return self.read_count * 0.02


class YTDLSource(disnake.PCMVolumeTransformer):
    def __init__(
        self, source: CustomAudioSource, *, data: dict[str, Any], volume: float = 0.5
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
            data = data["entries"][0]

        return cls(
            CustomAudioSource(
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
                f"[`{self.player.title}`]({'<' if hide_preview else ''}{self.player.original_url}{'>' if hide_preview else ''}) [**{format_duration(self.player.duration) if self.player.duration else 'live'}**]"
                + (f" (<@{self.trigger_message.author.id}>)" if show_queuer else "")
            )

    def embed(self, is_paused=False):
        progress = 0
        if self.player.duration:
            progress = self.player.original.progress / self.player.duration

        embed = disnake.Embed(
            color=constants.EMBED_COLOR,
            title=self.player.title,
            url=self.player.original_url,
            description=(
                f"{'⏸️ ' if is_paused else ''}"
                f"`[{'#'*int(progress * constants.BAR_LENGTH)}{'-'*int((1 - progress) * constants.BAR_LENGTH)}]` "
                + (
                    f"**{format_duration(int(self.player.original.progress))}** / **{format_duration(self.player.duration)}** (**{round(progress * 100)}%**)"
                    if self.player.duration
                    else "[**live**]"
                )
            ),
        )

        embed.add_field(
            name="Uploader",
            value=f"[{self.player.uploader}]({self.player.uploader_url})",
        )
        embed.add_field(name="Likes", value=f"{self.player.like_count:,}")
        embed.add_field(name="Views", value=f"{self.player.view_count:,}")
        embed.add_field(name="Published", value=f"<t:{self.player.timestamp}>")
        embed.add_field(name="Volume", value=f"{int(self.player.volume*100)}%")

        embed.set_image(self.player.thumbnail_url)
        embed.set_footer(
            text=f"queued by {self.trigger_message.author.name}",
            icon_url=(
                self.trigger_message.author.avatar.url
                if self.trigger_message.author.avatar
                else None
            ),
        )

        return embed

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


def format_duration(duration: int | float) -> str:
    hours, duration = divmod(int(duration), 3600)
    minutes, duration = divmod(duration, 60)
    segments = [hours, minutes, duration]
    if len(segments) == 3 and segments[0] == 0:
        del segments[0]
    return f"{':'.join(f'{s:0>2}' for s in segments)}"


def __reload_module__():
    global ytdl
    ytdl = yt_dlp.YoutubeDL(constants.YTDL_OPTIONS)
