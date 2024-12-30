import importlib
import inspect
import time

import arguments
import commands
import constants
import utils
from state import reloaded_modules, start_time


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


def __reload_module__():
    for name, module in globals().items():
        if (
            inspect.ismodule(module)
            and name not in constants.RELOAD_BLACKLISTED_MODULES
        ):
            importlib.reload(module)
            if "__reload_module__" in dir(module) and name not in reloaded_modules:
                reloaded_modules.add(name)
                module.__reload_module__()
