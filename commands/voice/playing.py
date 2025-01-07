import disnake
import disnake_paginator

import arguments
import commands
import constants
import utils
import youtubedl
from state import players

from .utils import command_allowed


async def playing(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0], "get information about the currently playing song"
    )
    parser.add_argument(
        "-d",
        "--description",
        action="store_true",
        help="get the description",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if not command_allowed(message, immutable=True):
        return

    if source := message.guild.voice_client.source:
        if args.description:
            if description := source.description:
                paginator = disnake_paginator.ButtonPaginator(
                    invalid_user_function=utils.invalid_user_handler,
                    color=constants.EMBED_COLOR,
                    title=source.title,
                    segments=disnake_paginator.split(description),
                )
                for embed in paginator.embeds:
                    embed.url = source.original_url
                await paginator.start(utils.MessageInteractionWrapper(message))
            else:
                await utils.reply(
                    message,
                    source.description or "no description found!",
                )
            return

        progress = source.original.progress / source.duration
        embed = disnake.Embed(
            color=constants.EMBED_COLOR,
            title=source.title,
            url=source.original_url,
            description=f"{'⏸️ ' if message.guild.voice_client.is_paused() else ''}"
            f"`[{'#'*int(progress * constants.BAR_LENGTH)}{'-'*int((1 - progress) * constants.BAR_LENGTH)}]` "
            f"**{youtubedl.format_duration(int(source.original.progress))}** / **{youtubedl.format_duration(source.duration)}** (**{round(progress * 100)}%**)",
        )
        embed.add_field(name="Volume", value=f"{int(source.volume*100)}%")
        embed.add_field(name="Views", value=f"{source.view_count:,}")
        embed.add_field(
            name="Queuer",
            value=players[message.guild.id].current.trigger_message.author.mention,
        )
        embed.set_image(source.thumbnail_url)

        await utils.reply(
            message,
            embed=embed,
        )
    else:
        await utils.reply(
            message,
            "nothing is playing!",
        )
