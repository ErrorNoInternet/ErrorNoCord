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
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-r",
        "--regex",
        required=False,
        help="delete messages with content matching this regex",
    )
    group.add_argument(
        "-c",
        "--contains",
        required=False,
        help="delete messages with content containing this substring",
    )
    parser.add_argument(
        "-i",
        "--case-insensitive",
        action="store_true",
        help="ignore case sensitivity when deleting messages",
    )
    parser.add_argument(
        "-a",
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
    parser.add_argument(
        "-d",
        "--delete-command",
        action="store_true",
        help="delete the command message as well",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if args.delete_command:
        try:
            await message.delete()
        except:
            pass

    regex = None
    if r := args.regex:
        regex = re.compile(r, re.IGNORECASE if args.case_insensitive else 0)

    def check(m):
        c = []
        if regex:
            c.append(regex.search(m.content))
        if s := args.contains:
            if args.case_insensitive:
                c.append(s.lower() in m.content.lower())
            else:
                c.append(s in m.content)
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

    if not args.delete_command:
        try:
            await utils.reply(
                message,
                f"purged **{messages}/{args.count} {'message' if args.count == 1 else 'messages'}**",
            )
        except:
            pass
