from logging import error

import disnake

import utils
from state import client, players


def play_after_callback(e, message, once):
    if e:
        error(f"player error: {e}")
    if not once:
        play_next(message)


def play_next(message, once=False, first=False):
    if not message.guild.voice_client:
        return
    message.guild.voice_client.stop()

    if not disnake.opus.is_loaded():
        utils.load_opus()

    if message.guild.id in players and players[message.guild.id].queue:
        queued = players[message.guild.id].queue_pop()
        message.guild.voice_client.play(
            queued.player, after=lambda e: play_after_callback(e, message, once)
        )

        embed = queued.embed()
        if first and len(players[message.guild.id].queue) == 0:
            client.loop.create_task(utils.reply(message, embed=embed))
        else:
            client.loop.create_task(utils.channel_send(message, embed=embed))


def remove_queued(messages):
    if messages[0].guild.id not in players:
        return

    if len(players[messages[0].guild.id].queue) == 0:
        return

    found = []
    for message in messages:
        for queued in players[message.guild.id].queue:
            if queued.trigger_message.id == message.id:
                found.append(queued)
    for queued in found:
        players[messages[0].guild.id].queue.remove(queued)


async def ensure_joined(message):
    if message.guild.voice_client is None:
        if message.author.voice:
            await message.author.voice.channel.connect()
        else:
            await utils.reply(message, "you are not connected to a voice channel!")


def command_allowed(message, immutable=False):
    if not message.guild.voice_client:
        return False

    if immutable:
        return True

    if not message.author.voice:
        return False

    return message.author.voice.channel.id == message.guild.voice_client.channel.id
