import time

import disnake

from utils import LimitedSizeDict

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
client = disnake.Client(intents=intents)

command_cooldowns = LimitedSizeDict()
command_locks = LimitedSizeDict()
idle_tracker = {"is_idle": False, "last_used": time.time()}
kill = {"transcript": False}
message_responses = LimitedSizeDict()
players = {}
sponsorblock_cache = LimitedSizeDict(size_limit=100)
start_time = time.time()
