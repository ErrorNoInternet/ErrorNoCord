import time

import disnake

start_time = time.time()

player_queue = {}

intents = disnake.Intents.default()
intents.message_content = True
client = disnake.Client(intents=intents)
