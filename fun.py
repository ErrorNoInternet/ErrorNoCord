import random


async def on_message(message):
    if "gn" in message.content:
        if random.random() < 0.01:
            await message.add_reaction(random.choice(["💤", "😪", "😴", "🛌"]))
