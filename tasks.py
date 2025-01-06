import asyncio
import time

import disnake

from state import client, idle_tracker, players


async def cleanup():
    while True:
        await asyncio.sleep(3600)

        targets = []
        for guild_id, player in players.items():
            if len(player.queue) == 0:
                targets.append(guild_id)
        for target in targets:
            del players[target]

        if (
            not idle_tracker["is_idle"]
            and time.time() - idle_tracker["last_used"] >= 3600
        ):
            await client.change_presence(status=disnake.Status.idle)
            idle_tracker["is_idle"] = True
