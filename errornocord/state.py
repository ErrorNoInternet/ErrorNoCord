import time

import disnake

from .utils import LimitedSizeDict

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
client = disnake.Client(intents=intents)

command_cooldowns = {}
command_locks = {}
idle_tracker = {"is_idle": False, "last_used": time.time()}
kill = {"transcript": False}
message_responses = LimitedSizeDict()
players = {}
sponsorblock_cache = LimitedSizeDict()
start_time = time.time()
trusted_users = []
