import contextlib
import importlib
import inspect
import time

import commands
import constants
import core
import events
from state import client, start_time


@client.event
async def on_ready():
    print(f"logged in as {client.user} in {round(time.time() - start_time, 1)}s")


@client.event
async def on_message_edit(before, after):
    await core.trigger_message_handlers("on_message_edit", before, after)

    await on_message(after)


@client.event
async def on_message(message):
    await core.trigger_message_handlers("on_message", message)

    global reloaded_modules

    if not message.content.startswith(constants.PREFIX):
        return

    if message.author.id in constants.OWNERS and commands.match(message.content) == [
        commands.Command.RELOAD
    ]:
        reloaded_modules = set()
        for module in filter(
            lambda v: inspect.ismodule(v)
            and v.__name__ not in constants.RELOAD_BLACKLISTED_MODULES,
            globals().values(),
        ):
            rreload(reloaded_modules, module)

        await message.add_reaction("✅")
        return

    await events.on_message(message)


def rreload(reloaded_modules, module):
    reloaded_modules.add(module)
    importlib.reload(module)
    if "__reload_module__" in dir(module):
        module.__reload_module__()

    with contextlib.suppress(AttributeError):
        for module in filter(
            lambda m: m.__spec__.origin != "frozen",
            filter(
                lambda v: inspect.ismodule(v)
                and (
                    v.__name__.split(".")[-1]
                    not in constants.RELOAD_BLACKLISTED_MODULES
                )
                and (v not in reloaded_modules),
                map(lambda attr: getattr(module, attr), dir(module)),
            ),
        ):
            rreload(reloaded_modules, module)


client.run(constants.SECRETS["TOKEN"])
