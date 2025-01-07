import arguments
import commands
import utils

from .utils import command_allowed


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
