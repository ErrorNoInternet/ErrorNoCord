import utils

from .utils import command_allowed


async def join(message):
    if message.author.voice:
        if message.guild.voice_client:
            await message.guild.voice_client.move_to(message.channel)
        else:
            await message.author.voice.channel.connect()
    else:
        await utils.reply(message, "you are not connected to a voice channel!")
        return

    await utils.add_check_reaction(message)


async def leave(message):
    if not command_allowed(message):
        return

    await message.guild.voice_client.disconnect()
    await utils.add_check_reaction(message)
