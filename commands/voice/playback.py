import arguments
import commands
import constants
import disnake_paginator
import utils
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

        await utils.reply(
            message,
            embed=players[message.guild.id].current.embed(
                is_paused=message.guild.voice_client.is_paused()
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
    parser = arguments.ArgumentParser(tokens[0], "fast forward audio playback")
    parser.add_argument(
        "seconds",
        type=lambda v: arguments.range_type(v, min=0, max=300),
        help="the amount of seconds to fast forward",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if not command_allowed(message):
        return

    if not message.guild.voice_client.source:
        await utils.reply(message, "nothing is playing!")
        return

    message.guild.voice_client.pause()
    message.guild.voice_client.source.original.fast_forward(args.seconds)
    message.guild.voice_client.resume()

    await utils.add_check_reaction(message)


async def volume(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(tokens[0], "get or set the current volume level")
    parser.add_argument(
        "volume",
        nargs="?",
        type=lambda v: arguments.range_type(v, min=0, max=150),
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
