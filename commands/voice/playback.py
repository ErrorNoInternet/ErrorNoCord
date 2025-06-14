import disnake_paginator

import arguments
import commands
import sponsorblock
import utils
from constants import EMBED_COLOR
from state import players

from .utils import command_allowed


async def playing(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0],
        "get information about the currently playing song",
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
                    color=EMBED_COLOR,
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

        await utils.reply(
            message,
            embed=players[message.guild.id].current.embed(
                is_paused=message.guild.voice_client.is_paused(),
            ),
        )
    else:
        await utils.reply(
            message,
            "nothing is playing!",
        )


async def resume(message):
    if not command_allowed(message):
        return

    if message.guild.voice_client.is_paused():
        message.guild.voice_client.resume()
        await utils.add_check_reaction(message)
    else:
        await utils.reply(
            message,
            "nothing is paused!",
        )


async def pause(message):
    if not command_allowed(message):
        return

    if message.guild.voice_client.is_playing():
        message.guild.voice_client.pause()
        await utils.add_check_reaction(message)
    else:
        await utils.reply(
            message,
            "nothing is playing!",
        )


async def fast_forward(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(tokens[0], "skip the current sponsorblock segment")
    parser.add_argument(
        "-s",
        "--seconds",
        nargs="?",
        type=lambda v: arguments.range_type(v, lower=0, upper=300),
        help="the number of seconds to fast forward instead",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if not command_allowed(message):
        return

    if not message.guild.voice_client.source:
        await utils.reply(message, "nothing is playing!")
        return

    seconds = args.seconds
    if not seconds:
        video = await sponsorblock.get_segments(
            players[message.guild.id].current.player.id,
        )
        if not video:
            await utils.reply(
                message,
                "no sponsorblock segments were found for this video!",
            )
            return

        progress = message.guild.voice_client.source.original.progress
        for segment in video["segments"]:
            begin, end = map(float, segment["segment"])
            if progress >= begin and progress < end:
                seconds = end - message.guild.voice_client.source.original.progress
        if not seconds:
            await utils.reply(message, "no sponsorblock segment is currently playing!")
            return

    message.guild.voice_client.pause()
    message.guild.voice_client.source.original.fast_forward(seconds)
    message.guild.voice_client.resume()

    await utils.add_check_reaction(message)


async def volume(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(tokens[0], "get or set the current volume level")
    parser.add_argument(
        "volume",
        nargs="?",
        type=lambda v: arguments.range_type(v, lower=0, upper=150),
        help="the volume level (0 - 150)",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if not command_allowed(message, immutable=True):
        return

    if not message.guild.voice_client.source:
        await utils.reply(message, "nothing is playing!")
        return

    if args.volume is None:
        await utils.reply(
            message,
            f"{int(message.guild.voice_client.source.volume * 100)}",
        )
    else:
        if not command_allowed(message):
            return

        message.guild.voice_client.source.volume = float(args.volume) / 100.0
        await utils.add_check_reaction(message)
