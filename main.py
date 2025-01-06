import time

import constants
import events
from state import client, start_time


@client.event
async def on_ready():
    print(f"logged in as {client.user} in {round(time.time() - start_time, 1)}s")

    await events.on_ready()


if __name__ == "__main__":
    client.run(constants.SECRETS["TOKEN"])
