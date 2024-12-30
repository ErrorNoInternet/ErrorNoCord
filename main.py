import time

import constants
import core
import events
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

    if not message.content.startswith(constants.PREFIX):
        return

    await core.on_message(message)


client.run(constants.SECRETS["TOKEN"])
