import core
import events
from state import client

dynamic_handlers = {}


async def trigger_dynamic_handlers(event_type: str, *data):
    if event_type in dynamic_handlers:
        for dynamic_handler in dynamic_handlers[event_type]:
            try:
                await dynamic_handler(*data)
            except Exception as e:
                print(
                    f"error in dynamic event handler {dynamic_handler} for {event_type}: {e}"
                )


@client.event
async def on_message_edit(before, after):
    await events.trigger_dynamic_handlers("on_message_edit", before, after)

    await core.on_message(after)


@client.event
async def on_message(message):
    await events.trigger_dynamic_handlers("on_message", message)

    await core.on_message(message)
