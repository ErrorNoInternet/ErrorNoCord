import asyncio
import time

import disnake

from state import client, last_used, players


async def check_idle():
    while True:
        await asyncio.sleep(3600)

        if time.time() - last_used >= 3600:
            await client.change_presence(status=disnake.Status.idle)
        else:
            await client.change_presence(status=disnake.Status.online)


async def cleanup():
    while True:
        await asyncio.sleep(3600)

        targets = []
        for id, player in players:
            if len(player.queue) == 0:
                targets.append(id)
        for target in targets:
            del players[target]
