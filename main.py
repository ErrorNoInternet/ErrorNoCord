import time

import constants
import events
from state import client, start_time


@client.event
async def on_ready():
    await events.trigger_dynamic_handlers("on_ready")
    print(f"logged in as {client.user} in {round(time.time() - start_time, 1)}s")


client.run(constants.SECRETS["TOKEN"])
