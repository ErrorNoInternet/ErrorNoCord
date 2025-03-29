import asyncio
import time
from logging import debug, error

import disnake

from state import client, idle_tracker, players


async def cleanup():
    debug("spawned cleanup thread")

    while True:
        await asyncio.sleep(3600 * 12)

        targets = []
        for guild_id, player in players.items():
            if len(player.queue) == 0:
                targets.append(guild_id)
        for target in targets:
            del players[target]
        debug(f"cleanup thread removed {len(targets)} empty players")

        if (
            not idle_tracker["is_idle"]
            and time.time() - idle_tracker["last_used"] >= 3600
        ):
            try:
                await client.change_presence(status=disnake.Status.idle)
                idle_tracker["is_idle"] = True
            except Exception as e:
                error(f"failed to change status to idle: {e}")
