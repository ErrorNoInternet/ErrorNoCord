import time

import arguments
import commands
import utils
from state import start_time


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
        await utils.reply(message, f"up {round(time.time() - start_time)} seconds")
