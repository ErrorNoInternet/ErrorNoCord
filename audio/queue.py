import collections
from dataclasses import dataclass
from typing import ClassVar, Optional

import disnake

from constants import BAR_LENGTH, EMBED_COLOR

from .utils import format_duration
from .youtubedl import YTDLSource


@dataclass
class Song:
    player: YTDLSource
    trigger_message: disnake.Message

    def format(self, show_queuer=False, hide_preview=False, multiline=False) -> str:
        title = f"[`{self.player.title}`]({'<' if hide_preview else ''}{self.player.original_url}{'>' if hide_preview else ''})"
        duration = (
            format_duration(self.player.duration) if self.player.duration else "stream"
        )
        if multiline:
            queue_time = (
                self.trigger_message.edited_at or self.trigger_message.created_at
            )
            return f"{title}\n**duration:** {duration}" + (
                f", **queued by:** <@{self.trigger_message.author.id}> <t:{round(queue_time.timestamp())}:R>"
                if show_queuer
                else ""
            )
        return f"{title} [**{duration}**]" + (
            f" (<@{self.trigger_message.author.id}>)" if show_queuer else ""
        )

    def embed(self, is_paused=False):
        progress = 0
        if self.player.duration:
            progress = self.player.original.progress / self.player.duration

        embed = disnake.Embed(
            color=EMBED_COLOR,
            title=self.player.title,
            url=self.player.original_url,
            description=(
                f"{'⏸️ ' if is_paused else ''}"
                f"`[{'#' * int(progress * BAR_LENGTH)}{'-' * int((1 - progress) * BAR_LENGTH)}]` "
                + (
                    f"**{format_duration(int(self.player.original.progress))}** / **{format_duration(self.player.duration)}** (**{round(progress * 100)}%**)"
                    if self.player.duration
                    else "[**stream**]"
                )
            ),
            timestamp=self.trigger_message.edited_at or self.trigger_message.created_at,
        )

        uploader_value = None
        if self.player.uploader_url:
            if self.player.uploader:
                uploader_value = f"[{self.player.uploader}]({self.player.uploader_url})"
            else:
                uploader_value = self.player.uploader_url
        elif self.player.uploader:
            uploader_value = self.player.uploader

        if uploader_value:
            embed.add_field(name="Uploader", value=uploader_value)
        if self.player.like_count:
            embed.add_field(name="Likes", value=f"{self.player.like_count:,}")
        if self.player.view_count:
            embed.add_field(name="Views", value=f"{self.player.view_count:,}")
        if self.player.timestamp:
            embed.add_field(name="Published", value=f"<t:{int(self.player.timestamp)}>")
        if self.player.volume:
            embed.add_field(name="Volume", value=f"{int(self.player.volume * 100)}%")

        if self.player.thumbnail_url:
            embed.set_image(self.player.thumbnail_url)

        embed.set_footer(
            text=f"Queued by {self.trigger_message.author.name}",
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
class Player:
    queue: ClassVar = collections.deque()
    current: Optional[Song] = None

    def queue_pop(self):
        popped = self.queue.popleft()
        self.current = popped
        return popped

    def queue_push(self, item):
        self.queue.append(item)

    def queue_push_front(self, item):
        self.queue.appendleft(item)

    def __str__(self):
        return self.__repr__()
