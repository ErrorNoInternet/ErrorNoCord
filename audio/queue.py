import collections
from dataclasses import dataclass
from typing import Optional

import disnake

from constants import BAR_LENGTH, EMBED_COLOR
from utils import format_duration

from .youtubedl import YTDLSource


@dataclass
class Song:
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
            color=EMBED_COLOR,
            title=self.player.title,
            url=self.player.original_url,
            description=(
                f"{'⏸️ ' if is_paused else ''}"
                f"`[{'#' * int(progress * BAR_LENGTH)}{'-' * int((1 - progress) * BAR_LENGTH)}]` "
                + (
                    f"**{format_duration(int(self.player.original.progress))}** / **{format_duration(self.player.duration)}** (**{round(progress * 100)}%**)"
                    if self.player.duration
                    else "[**live**]"
                )
            ),
        )

        if self.player.uploader_url:
            embed.add_field(
                name="Uploader",
                value=f"[{self.player.uploader}]({self.player.uploader_url})",
            )
        else:
            embed.add_field(
                name="Uploader",
                value=self.player.uploader,
            )
        embed.add_field(
            name="Likes",
            value=f"{self.player.like_count:,}"
            if self.player.like_count
            else "Unknown",
        )
        embed.add_field(name="Views", value=f"{self.player.view_count:,}")
        embed.add_field(name="Published", value=f"<t:{self.player.timestamp}>")
        embed.add_field(name="Volume", value=f"{int(self.player.volume * 100)}%")

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
class Player:
    queue = collections.deque()
    current: Optional[Song] = None

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
