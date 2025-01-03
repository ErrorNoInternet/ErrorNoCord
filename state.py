import time

import disnake

players = {}
command_locks = {}

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
client = disnake.Client(intents=intents)

start_time = time.time()
