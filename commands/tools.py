import re

import arguments

import commands
import utils


async def clear(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0],
        "bulk delete messages in the current channel matching certain criteria",
    )
    parser.add_argument(
        "count",
        type=int,
        choices=range(1, 1001),
        metavar="[1-1000]",
        help="amount of messages to delete",
    )
    parser.add_argument(
        "-r",
        "--regex",
        required=False,
        help="delete messages with content matching this regex",
    )
    parser.add_argument(
        "-i",
        "--author-id",
        type=int,
        action="append",
        help="delete messages whose author matches this id",
    )
    parser.add_argument(
        "-o",
        "--oldest-first",
        action="store_true",
        help="delete oldest messages first",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    def check(m):
        c = []
        if r := args.regex:
            c.append(re.match(r, m.content))
        if i := args.author_id:
            c.append(m.author.id in i)
        return all(c)

    message_count = len(
        await message.channel.purge(
            limit=args.count, check=check, oldest_first=args.oldest_first
        )
    )
    try:
        await utils.reply(
            message,
            f"purged **{message_count} {'message' if message_count == 1 else 'messages'}**",
        )
    except:
        pass
