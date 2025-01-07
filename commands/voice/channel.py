import utils

from .utils import command_allowed


async def join(message):
    if message.guild.voice_client:
        return await message.guild.voice_client.move_to(message.channel)

    await message.channel.connect()
    await utils.add_check_reaction(message)


async def leave(message):
    if not command_allowed(message):
        return

    await message.guild.voice_client.disconnect()
    await utils.add_check_reaction(message)
