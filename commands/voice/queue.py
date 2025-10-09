import itertools

import disnake
import disnake_paginator

import arguments
import audio
import commands
import utils
from constants import EMBED_COLOR
from state import client, players, trusted_users

from .playback import resume
from .utils import command_allowed, ensure_joined, play_next


async def queue_or_play(message, edited=False):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0],
        "queue a song, list the queue, or resume playback",
    )
    parser.add_argument("query", nargs="*", help="yt-dlp URL or query to get song")
    parser.add_argument(
        "-v",
        "--volume",
        default=50,
        type=lambda v: arguments.range_type(v, lower=0, upper=150),
        help="the volume level (0 - 150) for the specified song",
    )
    parser.add_argument(
        "-i",
        "--remove-index",
        type=int,
        nargs="*",
        help="remove queued songs by index",
    )
    parser.add_argument(
        "-m",
        "--match-multiple",
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

    await ensure_joined(message)
    if len(tokens) == 1 and tokens[0].lower() != "play":
        if not command_allowed(message, immutable=True):
            return
    elif not command_allowed(message):
        return

    if message.guild.id not in players:
        players[message.guild.id] = audio.queue.Player()

    if edited:
        found = next(
            filter(
                lambda queued: queued.trigger_message.id == message.id,
                players[message.guild.id].queue,
            ),
            None,
        )
        if found:
            players[message.guild.id].queue.remove(found)

    if args.clear:
        players[message.guild.id].queue.clear()
        await utils.add_check_reaction(message)
    elif indices := args.remove_index:
        targets = []
        for i in indices:
            if i <= 0 or i > len(players[message.guild.id].queue):
                await utils.reply(message, f"invalid index `{i}`!")
                return
            targets.append(players[message.guild.id].queue[i - 1])

        for target in targets:
            if target in players[message.guild.id].queue:
                players[message.guild.id].queue.remove(target)

        if len(targets) == 1:
            await utils.reply(message, f"**removed** {targets[0].format()}")
        else:
            await utils.reply(
                message,
                f"removed **{len(targets)}** queued {'song' if len(targets) == 1 else 'songs'}",
            )
    elif args.remove_title or args.remove_queuer:
        targets = set()
        for queued in players[message.guild.id].queue:
            if t := args.remove_title:
                if t in queued.player.title:
                    targets.add(queued)
            if q := args.remove_queuer:
                if q == queued.trigger_message.author.id:
                    targets.add(queued)
        targets = list(targets)
        if not args.match_multiple:
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
                    ),
                ),
            )
            >= 5
            and not len(message.guild.voice_client.channel.members) == 2
            and message.author.id not in trusted_users
        ):
            await utils.reply(
                message,
                "you can only queue **5 items** without the manage channels permission!",
            )
            return

        try:
            async with message.channel.typing():
                player = await audio.youtubedl.YTDLSource.from_url(
                    " ".join(query),
                    loop=client.loop,
                    stream=True,
                )
                player.volume = float(args.volume) / 100.0
        except Exception as e:
            await utils.reply(message, f"failed to queue: `{e}`")
            return

        queued = audio.queue.Song(player, message)

        if args.now or args.next:
            players[message.guild.id].queue_push_front(queued)
        else:
            players[message.guild.id].queue_push(queued)

        if not message.guild.voice_client:
            await utils.reply(message, "unexpected disconnect from voice channel!")
            return
        elif not message.guild.voice_client.source:
            play_next(message, first=True)
        elif args.now:
            message.guild.voice_client.stop()
        else:
            await utils.reply(
                message,
                f"**{1 if args.next else len(players[message.guild.id].queue)}.** {queued.format()}",
            )

        utils.cooldown(message, 2)
    elif tokens[0].lower() == "play":
        await resume(message)
    else:
        if players[message.guild.id].queue:
            formatted_duration = utils.format_duration(
                sum(
                    [
                        queued.player.duration if queued.player.duration else 0
                        for queued in players[message.guild.id].queue
                    ],
                ),
                natural=True,
            )

            def embed(description):
                e = disnake.Embed(
                    description=description,
                    color=EMBED_COLOR,
                )
                if formatted_duration and len(players[message.guild.id].queue) > 1:
                    e.set_footer(text=f"{formatted_duration} in total")
                return e

            await disnake_paginator.ButtonPaginator(
                invalid_user_function=utils.invalid_user_handler,
                color=EMBED_COLOR,
                segments=list(
                    map(
                        embed,
                        [
                            "\n\n".join(
                                [
                                    f"**{i + 1}.** {queued.format(show_queuer=True, hide_preview=True, multiline=True)}"
                                    for i, queued in batch
                                ],
                            )
                            for batch in itertools.batched(
                                enumerate(players[message.guild.id].queue),
                                10,
                            )
                        ],
                    ),
                ),
            ).start(utils.MessageInteractionWrapper(message))
        else:
            await utils.reply(
                message,
                "nothing is queued!",
            )


async def skip(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(tokens[0], "skip the song currently playing")
    parser.add_argument(
        "-n",
        "--next",
        action="store_true",
        help="skip the next song",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if not command_allowed(message):
        return

    if not players[message.guild.id] or not players[message.guild.id].queue:
        message.guild.voice_client.stop()
        await utils.reply(
            message,
            "the queue is empty now!",
        )
    elif args.next:
        next = players[message.guild.id].queue.pop()
        await utils.reply(message, f"**skipped** {next.format()}")
    else:
        message.guild.voice_client.stop()
        await utils.add_check_reaction(message)
        if not message.guild.voice_client.source:
            play_next(message)
