import asyncio
import threading

import commands
import core
import tasks
from state import client


async def on_ready():
    threading.Thread(
        name="cleanup",
        target=asyncio.run_coroutine_threadsafe,
        args=(
            tasks.cleanup(),
            client.loop,
        ),
    ).start()

    threading.Thread(
        name="check_idle",
        target=asyncio.run_coroutine_threadsafe,
        args=(
            tasks.check_idle(),
            client.loop,
        ),
    ).start()


async def on_message(message):
    await core.on_message(message)


async def on_message_edit(before, after):
    if before.content == after.content:
        return

    await core.on_message(after, edited=True)


async def on_message_delete(message):
    commands.voice.delete_queued([message])


async def on_bulk_message_delete(messages):
    commands.voice.delete_queued(messages)


async def on_voice_state_update(member, before, after):
    await core.on_voice_state_update(member, before, after)


for k, v in client.get_listeners().items():
    for f in v:
        client.remove_listener(f, k)

client.add_listener(on_bulk_message_delete, "on_bulk_message_delete")
client.add_listener(on_message, "on_message")
client.add_listener(on_message_delete, "on_message_delete")
client.add_listener(on_message_edit, "on_message_edit")
client.add_listener(on_voice_state_update, "on_voice_state_update")
