import importlib
import inspect
import time

import commands
import constants
import core
import events
from state import client, reloaded_modules, start_time


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
        for name, module in globals().items():
            if (
                inspect.ismodule(module)
                and name not in constants.RELOAD_BLACKLISTED_MODULES
            ):
                importlib.reload(module)
                if "__reload_module__" in dir(module) and name not in reloaded_modules:
                    reloaded_modules.add(name)
                    module.__reload_module__()
        reloaded_modules.clear()
        await message.add_reaction("✅")
        return

    await events.on_message(message)


client.run(constants.SECRETS["TOKEN"])
