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

        days, duration = divmod(duration, 86400)
        if days >= 1:
            days = int(days)
            segments.append(f"{days} {format_plural('day', days)}")

        hours, duration = divmod(duration, 3600)
        if hours >= 1:
            hours = int(hours)
            segments.append(f"{hours} {format_plural('hour', hours)}")

        minutes, duration = divmod(duration, 60)
        if minutes >= 1:
            minutes = int(minutes)
            segments.append(f"{minutes} {format_plural('minute', minutes)}")

        seconds = int(duration)
        if seconds > 0:
            segments.append(f"{seconds} {format_plural('second', seconds)}")

        await utils.reply(message, f"up {', '.join(segments)}")
