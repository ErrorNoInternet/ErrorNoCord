import core
import events
from state import client

dynamic_handlers = {}


async def trigger_dynamic_handlers(event_type: str, *data):
    if event_type in dynamic_handlers:
        for dynamic_handler in dynamic_handlers[event_type]:
            await dynamic_handler(*data)


@client.event
async def on_message_edit(before, after):
    await events.trigger_dynamic_handlers("on_message_edit", before, after)

    await core.on_message(after)


@client.event
async def on_message(message):
    await events.trigger_dynamic_handlers("on_message", message)

    await core.on_message(message)
