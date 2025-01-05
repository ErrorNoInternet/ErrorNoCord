import time

import disnake

command_locks = {}
executed_messages = {}
players = {}

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
client = disnake.Client(intents=intents)

start_time = time.time()
