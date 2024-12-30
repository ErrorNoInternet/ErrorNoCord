import re

import commands


async def clear(message):
    tokens = commands.tokenize(message.content)[1:]
    if len(tokens) < 2:
        await message.reply("no count and/or regex supplied!", mention_author=False)
        return

    message_count = len(
        await message.channel.purge(
            limit=int(tokens[0]), check=lambda m: re.match(tokens[1], m.content)
        )
    )
    try:
        await message.reply(
            f"successfully purged **{message_count} {'message' if message_count == 1 else 'messages'}**",
            mention_author=False,
        )
    except:
        pass
