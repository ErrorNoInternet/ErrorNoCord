import time

import arguments
import commands
import utils
from state import start_time


async def help(message):
    await utils.reply(
        message,
        ", ".join(
            [f"`{command.value}`" for command in commands.Command.__members__.values()]
        ),
    )


async def uptime(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0],
        "print bot uptime",
    )
    parser.add_argument(
        "-s",
        "--since",
        action="store_true",
        help="bot up since",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if args.since:
        await utils.reply(message, f"{round(start_time)}")
    else:
        format_plural = lambda noun, count: noun if count == 1 else noun + "s"

        segments = []
        duration = time.time() - start_time
        if duration >= 86400:
            d = int(duration // 86400)
            segments.append(f"{d} {format_plural('day', d)}")
            duration %= 86400
        if duration >= 3600:
            h = int(duration // 3600)
            segments.append(f"{h} {format_plural('hour', h)}")
            duration %= 3600
        if duration >= 60:
            m = int(duration // 60)
            segments.append(f"{m} {format_plural('minute', m)}")
            duration %= 60
        if duration > 0:
            s = int(duration)
            segments.append(f"{s} {format_plural('second', s)}")

        await utils.reply(message, f"up {', '.join(segments)}")
