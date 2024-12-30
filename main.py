import inspect
import time

import commands
import constants
import core
import events
import utils
from state import client, start_time


@client.event
async def on_ready():
    print(f"logged in as {client.user} in {round(time.time() - start_time, 1)}s")


@client.event
async def on_message_edit(before, after):
    await events.trigger_dynamic_handlers("on_message_edit", before, after)

    await on_message(after)


@client.event
async def on_message(message):
    await events.trigger_dynamic_handlers("on_message", message)

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
            core.rreload(reloaded_modules, module)

        await utils.add_check_reaction(message)
        return

    await core.on_message(message)


client.run(constants.SECRETS["TOKEN"])
