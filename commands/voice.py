import functools

import arguments
import commands
import utils
import youtubedl
from state import client, player_current, player_queue


async def queue_or_play(message):
    await ensure_joined(message)
    if not command_allowed(message):
        return

    if message.guild.id not in player_queue:
        player_queue[message.guild.id] = []

    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0], "queue a song, list the queue, or resume playback"
    )
    parser.add_argument("query", nargs="?", help="yt-dlp URL or query to get song")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v",
        "--volume",
        default=50,
        type=functools.partial(arguments.range_type, min=0, max=150),
        metavar="[0-150]",
        help="the volume level (0 - 150)",
    )
    group.add_argument(
        "-i",
        "--remove-index",
        type=int,
        help="remove a queued song by index",
    )
    group.add_argument(
        "-m",
        "--remove-multiple",
        action="store_true",
        help="continue removing queued songs after finding a match",
    )
    group.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="remove all queued songs",
    )
    parser.add_argument(
        "-t",
        "--remove-title",
        help="remove queued songs by title",
    )
    parser.add_argument(
        "-q",
        "--remove-queuer",
        type=int,
        help="remove queued songs by queuer",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if args.clear:
        player_queue[message.guild.id] = []
        await utils.add_check_reaction(message)
        return
    elif i := args.remove_index:
        try:
            queued = player_queue[message.guild.id][i - 1]
            del player_queue[message.guild.id][i - 1]
            await utils.reply(message, f"**x** `{queued['player'].title}`")
        except:
            await utils.reply(message, "invalid index!")
    elif args.remove_title or args.remove_queuer:
        targets = []
        for queued in player_queue[message.guild.id]:
            if t := args.remove_title:
                if t in queued["player"].title:
                    targets.append(queued)
            if q := args.remove_queuer:
                if q == queued["queuer"]:
                    targets.append(queued)
        if not args.remove_multiple:
            targets = targets[:1]
        for target in targets:
            if target in player_queue[message.guild.id]:
                player_queue[message.guild.id].remove(target)
        await utils.reply(
            message,
            f"removed **{len(targets)}** queued {'song' if len(targets) == 1 else 'songs'}",
        )
    elif query := args.query:
        try:
            async with message.channel.typing():
                player = await youtubedl.YTDLSource.from_url(
                    query, loop=client.loop, stream=True
                )
                player.volume = float(args.volume) / 100.0
        except Exception as e:
            await utils.reply(
                message,
                f"**unable to queue {query}:** {e}",
            )
            return

        player_queue[message.guild.id].insert(
            0, {"player": player, "queuer": message.author.id}
        )

        if (
            not message.guild.voice_client.is_playing()
            and not message.guild.voice_client.is_paused()
        ):
            await utils.reply(message, f"**0.** `{player.title}`")
            play_next(message)
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
                    lambda: f"**0.** {'(paused) ' if message.guild.voice_client.is_paused() else ''}`{message.guild.voice_client.source.title}` (<@{player_current[message.guild.id]['queuer']}>)"
                )
                if (
                    not player_queue[message.guild.id]
                    and not message.guild.voice_client.source
                ):
                    await utils.reply(
                        message,
                        "nothing is playing or queued!",
                    )
                elif not player_queue[message.guild.id]:
                    await utils.reply(message, generate_currently_playing())
                elif not message.guild.voice_client.source:
                    await utils.reply(
                        message,
                        generate_queue_list(player_queue[message.guild.id]),
                    )
                else:
                    await utils.reply(
                        message,
                        generate_currently_playing()
                        + "\n"
                        + generate_queue_list(player_queue[message.guild.id]),
                    )
        else:
            await utils.reply(
                message,
                "nothing is currently queued!",
            )


async def skip(message):
    if not command_allowed(message):
        return

    if not player_queue[message.guild.id]:
        message.guild.voice_client.stop()
        await utils.reply(
            message,
            "the queue is empty now!",
        )
    else:
        message.guild.voice_client.stop()
        await utils.add_check_reaction(message)


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
        type=functools.partial(arguments.range_type, min=0, max=150),
        metavar="[0-150]",
        help="the volume level (0 - 150)",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if not message.guild.voice_client.source:
        await utils.reply(
            message,
            f"there is no player currently active!",
        )
        return

    if args.volume is None:
        await utils.reply(
            message,
            f"{int(message.guild.voice_client.source.volume * 100)}",
        )
    else:
        message.guild.voice_client.source.volume = float(args.volume) / 100.0
        await utils.add_check_reaction(message)


def play_next(message, once=False):
    message.guild.voice_client.stop()
    if player_queue[message.guild.id]:
        queued = player_queue[message.guild.id][0]
        del player_queue[message.guild.id][0]
        player_current[message.guild.id] = queued
        message.guild.voice_client.play(
            queued["player"], after=lambda _: play_next(message) if not once else None
        )


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
