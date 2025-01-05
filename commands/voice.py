import itertools

import disnake
import disnake_paginator

import arguments
import commands
import constants
import utils
import youtubedl
from state import client, players


async def queue_or_play(message):
    await ensure_joined(message)
    if not command_allowed(message):
        return

    if message.guild.id not in players:
        players[message.guild.id] = youtubedl.QueuedPlayer()

    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0], "queue a song, list the queue, or resume playback"
    )
    parser.add_argument("query", nargs="?", help="yt-dlp URL or query to get song")
    parser.add_argument(
        "-v",
        "--volume",
        default=50,
        type=lambda v: arguments.range_type(v, min=0, max=150),
        help="the volume level (0 - 150) for the specified song",
    )
    parser.add_argument(
        "-i",
        "--remove-index",
        type=int,
        help="remove a queued song by index",
    )
    parser.add_argument(
        "-m",
        "--remove-multiple",
        action="store_true",
        help="continue removing queued after finding a match",
    )
    parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="remove all queued songs",
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="play the specified song immediately",
    )
    parser.add_argument(
        "--next",
        action="store_true",
        help="play the specified song next",
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
        players[message.guild.id].queue.clear()
        await utils.add_check_reaction(message)
        return
    elif i := args.remove_index:
        if i <= 0 or i > len(players[message.guild.id].queue):
            await utils.reply(message, "invalid index!")
            return

        queued = players[message.guild.id].queue[i - 1]
        del players[message.guild.id].queue[i - 1]
        await utils.reply(message, f"**X** {queued.format()}")
    elif args.remove_title or args.remove_queuer:
        targets = []
        for queued in players[message.guild.id].queue:
            if t := args.remove_title:
                if t in queued.player.title:
                    targets.append(queued)
                    continue
            if q := args.remove_queuer:
                if q == queued.trigger_message.author.id:
                    targets.append(queued)
        if not args.remove_multiple:
            targets = targets[:1]

        for target in targets:
            players[message.guild.id].queue.remove(target)
        await utils.reply(
            message,
            f"removed **{len(targets)}** queued {'song' if len(targets) == 1 else 'songs'}",
        )
    elif query := args.query:
        if (
            not message.channel.permissions_for(message.author).manage_channels
            and len(
                list(
                    filter(
                        lambda queued: queued.trigger_message.author.id
                        == message.author.id,
                        players[message.guild.id].queue,
                    )
                )
            )
            >= 5
        ):
            await utils.reply(
                message,
                "you can only queue **5 songs** without the manage channels permission!",
            )
            return

        try:
            async with message.channel.typing():
                player = await youtubedl.YTDLSource.from_url(
                    query, loop=client.loop, stream=True
                )
                player.volume = float(args.volume) / 100.0
        except Exception as e:
            await utils.reply(
                message, f"**failed to queue:** `{e}`", suppress_embeds=True
            )
            return

        queued = youtubedl.QueuedSong(player, message)

        if args.now or args.next:
            players[message.guild.id].queue_add_front(queued)
        else:
            players[message.guild.id].queue_add(queued)

        if (
            not message.guild.voice_client.is_playing()
            and not message.guild.voice_client.is_paused()
        ):
            play_next(message)
        elif args.now:
            message.guild.voice_client.stop()
        else:
            await utils.reply(
                message,
                f"**{len(players[message.guild.id].queue)}.** {queued.format()}",
            )
    else:
        if tokens[0].lower() == "play":
            await resume(message)
        else:
            if players[message.guild.id].queue:
                formatted_duration = utils.format_duration(
                    sum(
                        [
                            queued.player.duration if queued.player.duration else 0
                            for queued in players[message.guild.id].queue
                        ]
                    )
                )

                def embed(description):
                    e = disnake.Embed(
                        title="Queued",
                        description=description,
                        color=constants.EMBED_COLOR,
                    )
                    if formatted_duration:
                        e.set_footer(text=f"{formatted_duration} long")
                    return e

                await disnake_paginator.ButtonPaginator(
                    invalid_user_function=utils.invalid_user_handler,
                    color=constants.EMBED_COLOR,
                    segments=list(
                        map(
                            embed,
                            [
                                "\n\n".join(
                                    [
                                        f"**{i + 1}.** {queued.format(show_queuer=True, hide_preview=True, multiline=True)}"
                                        for i, queued in batch
                                    ]
                                )
                                for batch in itertools.batched(
                                    enumerate(players[message.guild.id].queue), 10
                                )
                            ],
                        )
                    ),
                ).start(disnake_paginator.wrappers.MessageInteractionWrapper(message))
            else:
                await utils.reply(
                    message,
                    "nothing is queued!",
                )


async def playing(message):
    if not command_allowed(message):
        return

    if message.guild.voice_client.source:
        await utils.reply(
            message,
            f"{'(paused) ' if message.guild.voice_client.is_paused() else ''} {players[message.guild.id].current.format(show_queuer=True)}",
        )
    else:
        await utils.reply(
            message,
            "nothing is playing!",
        )


async def skip(message):
    if not command_allowed(message):
        return

    if not players[message.guild.id].queue:
        message.guild.voice_client.stop()
        await utils.reply(
            message,
            "the queue is empty now!",
        )
    else:
        message.guild.voice_client.stop()
        await utils.add_check_reaction(message)
        if (
            not message.guild.voice_client.is_playing()
            and not message.guild.voice_client.is_paused()
        ):
            play_next(message)


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
        type=lambda v: arguments.range_type(v, min=0, max=150),
        help="the volume level (0 - 150)",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if not message.guild.voice_client.source:
        await utils.reply(
            message,
            f"nothing is playing!",
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


def play_after_callback(e, message, once):
    if e:
        print(f"player error: {e}")
    if not once:
        play_next(message)


def play_next(message, once=False):
    message.guild.voice_client.stop()
    if players[message.guild.id].queue:
        queued = players[message.guild.id].queue_pop()
        try:
            message.guild.voice_client.play(
                queued.player, after=lambda e: play_after_callback(e, message, once)
            )
        except Exception as e:
            client.loop.create_task(
                message.channel.send(f"error while trying to play: `{e}`")
            )
            return
        client.loop.create_task(
            message.channel.send(f"**0.** {queued.format(show_queuer=True)}")
        )


async def ensure_joined(message):
    if message.guild.voice_client is None:
        if message.author.voice:
            await message.author.voice.channel.connect()
        else:
            await utils.reply(message, "You are not connected to a voice channel.")


def command_allowed(message):
    if not message.author.voice or not message.guild.voice_client:
        return False
    return message.author.voice.channel.id == message.guild.voice_client.channel.id
