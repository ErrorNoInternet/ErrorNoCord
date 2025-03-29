import random

import commands
from constants import REACTIONS


async def on_message(message):
    if random.random() < 0.01:
        tokens = commands.tokenize(message.content, remove_prefix=False)
        for keyword, options in REACTIONS.items():
            if keyword in tokens:
                await message.add_reaction(random.choice(options))
                break
