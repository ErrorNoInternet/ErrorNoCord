import importlib
import inspect

import arguments
import commands
import constants
import utils
import ytdlp
from state import client, playback_queue, reloaded_modules


async def queue_or_play(message):
    await ensure_joined(message)
    if not command_allowed(message):
        return

    if message.guild.id not in playback_queue:
        playback_queue[message.guild.id] = []

    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0], "queue a song, list the queue, or resume playback"
    )
    parser.add_argument("query", nargs="?", help="yt-dlp URL or query to get song")
    parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="clear all queued songs",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if args.clear:
        playback_queue[message.guild.id] = []
        await message.add_reaction("✅")
        return
    elif query := args.query:
        try:
            async with message.channel.typing():
                player = await ytdlp.YTDLSource.from_url(
                    query, loop=client.loop, stream=True
                )
        except Exception as e:
            await utils.reply(
                message,
                f"**unable to queue {query}:** {e}",
            )
            return

        playback_queue[message.guild.id].append(
            {"player": player, "queuer": message.author.id}
        )

        if (
            not message.guild.voice_client.is_playing()
            and not message.guild.voice_client.is_paused()
        ):
            await play_next(message)
        else:
            await utils.reply(
                message,
                f"**+** `{player.title}`",
            )
    else:
        if message.guild.voice_client:
            if tokens[0].lower() == "play":
                message.guild.voice_client.resume()
                await utils.reply(
                    message,
                    "resumed!",
                )
            else:
                generate_currently_playing = (
                    lambda: f"**0.** {'**paused:** ' if message.guild.voice_client.is_paused() else ''}`{message.guild.voice_client.source.title}`"
                )
                if (
                    not playback_queue[message.guild.id]
                    and not message.guild.voice_client.source
                ):
                    await utils.reply(
                        message,
                        "nothing is playing or queued!",
                    )
                elif not playback_queue[message.guild.id]:
                    await utils.reply(message, generate_currently_playing())
                elif not message.guild.voice_client.source:
                    await utils.reply(
                        message,
                        generate_queue_list(playback_queue[message.guild.id]),
                    )
                else:
                    await utils.reply(
                        message,
                        generate_currently_playing()
                        + "\n"
                        + generate_queue_list(playback_queue[message.guild.id]),
                    )
        else:
            await utils.reply(
                message,
                "nothing is currently queued!",
            )


async def skip(message):
    if not command_allowed(message):
        return

    if not playback_queue[message.guild.id]:
        message.guild.voice_client.stop()
        await utils.reply(
            message,
            "the queue is empty now!",
        )
    else:
        await play_next(message)


async def join(message):
    if message.guild.voice_client:
        return await message.guild.voice_client.move_to(message.channel)

    await message.channel.connect()


async def leave(message):
    if not command_allowed(message):
        return

    await message.guild.voice_client.disconnect()


async def resume(message):
    if not command_allowed(message):
        return

    message.guild.voice_client.resume()
    await utils.reply(
        message,
        "resumed!",
    )


async def pause(message):
    if not command_allowed(message):
        return

    message.guild.voice_client.pause()
    await utils.reply(
        message,
        "paused!",
    )


async def volume(message):
    if not command_allowed(message):
        return

    if not message.guild.voice_client:
        return

    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(tokens[0], "set the current volume level")
    parser.add_argument(
        "volume",
        nargs="?",
        type=int,
        choices=range(0, 151),
        metavar="[0-150]",
        help="the volume level (0 - 150)",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if args.volume:
        message.guild.voice_client.source.volume = float(args.volume) / 100.0
        await utils.reply(
            message,
            f"volume set to **{args.volume}%**",
        )
    else:
        if message.guild.voice_client.source:
            await utils.reply(
                message,
                f"current volume is **{int(message.guild.voice_client.source.volume * 100)}%**",
            )
        else:
            await utils.reply(
                message,
                f"there is no player currently active!",
            )


async def play_next(message):
    while playback_queue[message.guild.id]:
        queued = playback_queue[message.guild.id].pop()
        await ensure_joined(message)
        message.guild.voice_client.stop()
        message.guild.voice_client.play(
            queued["player"], after=lambda e: print(f"player error: {e}") if e else None
        )
        await message.channel.send(f"**now playing:** {queued['player'].title}")


async def ensure_joined(message):
    if message.guild.voice_client is None:
        if message.author.voice:
            await message.author.voice.channel.connect()
        else:
            await utils.reply(message, "You are not connected to a voice channel.")


def command_allowed(message):
    if not message.guild.voice_client:
        return False
    return message.author.voice.channel.id == message.guild.voice_client.channel.id


def generate_queue_list(queue: list):
    return "\n".join(
        [
            f"**{i + 1}.** `{queued['player'].title}` (<@{queued['queuer']}>)"
            for i, queued in enumerate(queue)
        ]
    )


def __reload_module__():
    for name, module in globals().items():
        if (
            inspect.ismodule(module)
            and name not in constants.RELOAD_BLACKLISTED_MODULES
        ):
            importlib.reload(module)
            if "__reload_module__" in dir(module) and name not in reloaded_modules:
                reloaded_modules.add(name)
                module.__reload_module__()
