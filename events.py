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


async def on_message(message):
    await events.trigger_dynamic_handlers("on_message", message)

    await core.on_message(message)


async def on_message_edit(before, after):
    await events.trigger_dynamic_handlers("on_message_edit", before, after)

    if before.content == after.content:
        return

    await core.on_message(after)


async def on_voice_state_update(member, before, after):
    await events.trigger_dynamic_handlers(
        "on_voice_state_update", member, before, after
    )

    await core.on_voice_state_update(member, before, after)


for k, v in client.get_listeners().items():
    for f in v:
        client.remove_listener(f, k)
client.add_listener(on_message, "on_message")
client.add_listener(on_message_edit, "on_message_edit")
client.add_listener(on_voice_state_update, "on_voice_state_update")
