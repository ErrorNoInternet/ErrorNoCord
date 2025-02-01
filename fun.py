import random

import commands


async def on_message(message):
    if random.random() < 0.01 and "gn" in commands.tokenize(
        message.content, remove_prefix=False
    ):
        await message.add_reaction(random.choice(["💤", "😪", "😴", "🛌"]))
