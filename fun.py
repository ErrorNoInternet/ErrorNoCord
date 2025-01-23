import random

import commands


async def on_message(message):
    if "gn" in commands.tokenize(message.content, remove_prefix=False):
        if random.random() < 0.01:
            await message.add_reaction(random.choice(["💤", "😪", "😴", "🛌"]))
