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
        type=lambda c: arguments.range_type(c, min=1, max=1000),
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
    parser.add_argument(
        "-R",
        "--reactions",
        action="store_true",
        help="delete messages with reactions",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    def check(m):
        c = []
        if r := args.regex:
            c.append(re.match(r, m.content))
        if i := args.author_id:
            c.append(m.author.id in i)
        if args.reactions:
            c.append(len(m.reactions) > 0)
        return all(c)

    messages = len(
        await message.channel.purge(
            limit=args.count, check=check, oldest_first=args.oldest_first
        )
    )

    try:
        await utils.reply(
            message,
            f"purged **{messages}/{args.count} {'message' if args.count == 1 else 'messages'}**",
        )
    except:
        pass
