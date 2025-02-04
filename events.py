import asyncio
import threading
from logging import debug, info, warning

import commands
import core
import fun
import tasks
from state import client


def prepare():
    threading.Thread(
        name="cleanup",
        target=asyncio.run_coroutine_threadsafe,
        args=(
            tasks.cleanup(),
            client.loop,
        ),
    ).start()


async def on_bulk_message_delete(messages):
    commands.voice.remove_queued(messages)


async def on_message(message):
    await core.on_message(message)
    await fun.on_message(message)


async def on_message_delete(message):
    commands.voice.remove_queued([message])


async def on_message_edit(before, after):
    if before.content == after.content:
        return

    await core.on_message(after, edited=True)


async def on_voice_state_update(member, before, after):
    await core.on_voice_state_update(member, before, after)


async def on_ready():
    info(f"logged in as {client.user}")


async def on_connect():
    debug("connected to the gateway!")


async def on_disconnect():
    warning("disconnected from the gateway!")


for event_type, handlers in client.get_listeners().items():
    for handler in handlers:
        client.remove_listener(handler, event_type)

client.add_listener(on_bulk_message_delete, "on_bulk_message_delete")
client.add_listener(on_connect, "on_connect")
client.add_listener(on_disconnect, "on_disconnect")
client.add_listener(on_message, "on_message")
client.add_listener(on_message_delete, "on_message_delete")
client.add_listener(on_message_edit, "on_message_edit")
client.add_listener(on_ready, "on_ready")
client.add_listener(on_voice_state_update, "on_voice_state_update")
