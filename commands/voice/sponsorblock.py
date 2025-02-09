import disnake

import audio
import sponsorblock
import utils
from constants import EMBED_COLOR
from state import players

from .utils import command_allowed


async def sponsorblock_command(message):
    if not command_allowed(message, immutable=True):
        return

    if not message.guild.voice_client.source:
        await utils.reply(message, "nothing is playing!")
        return

    progress = message.guild.voice_client.source.original.progress
    video = await sponsorblock.get_segments(players[message.guild.id].current.player.id)
    if not video:
        await utils.reply(
            message, "no sponsorblock segments were found for this video!"
        )
        return

    text = []
    for segment in video["segments"]:
        begin, end = map(int, segment["segment"])
        category_name = sponsorblock.CATEGORY_NAMES.get(segment["category"])

        current = "**" if progress >= begin and progress < end else ""
        text.append(
            f"{current}`{audio.utils.format_duration(begin)}` - `{audio.utils.format_duration(end)}`: {category_name if category_name else 'Unknown'}{current}"
        )

    await utils.reply(
        message,
        embed=disnake.Embed(
            title="Sponsorblock segments",
            description="\n".join(text),
            color=EMBED_COLOR,
        ),
    )
