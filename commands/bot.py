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
        await utils.reply(
            message, f"up {utils.format_duration(int(time.time() - start_time))}"
        )
