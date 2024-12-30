import time

import disnake

player_queue = {}
player_current = {}
command_locks = {}

intents = disnake.Intents.default()
intents.message_content = True
client = disnake.Client(intents=intents)

start_time = time.time()
