import constants
import disnake
import youtubedl
from state import client, players

import utils


def play_after_callback(e, message, once):
    if e:
        print(f"player error: {e}")
    if not once:
        play_next(message)


def play_next(message, once=False, first=False):
    if not message.guild.voice_client:
        return

    message.guild.voice_client.stop()
    if message.guild.id in players and players[message.guild.id].queue:
        queued = players[message.guild.id].queue_pop()
        try:
            message.guild.voice_client.play(
                queued.player, after=lambda e: play_after_callback(e, message, once)
            )
        except disnake.opus.OpusNotLoaded:
            utils.load_opus()
            message.guild.voice_client.play(
                queued.player, after=lambda e: play_after_callback(e, message, once)
            )

        embed = disnake.Embed(
            color=constants.EMBED_COLOR,
            title=queued.player.title,
            url=queued.player.original_url,
            description=f"`[{'-'*constants.BAR_LENGTH}]` **{youtubedl.format_duration(0)}** / **{youtubedl.format_duration(queued.player.duration)}**",
        )
        embed.add_field(name="Volume", value=f"{int(queued.player.volume*100)}%")
        embed.add_field(name="Views", value=f"{queued.player.view_count:,}")
        embed.add_field(
            name="Queuer",
            value=players[message.guild.id].current.trigger_message.author.mention,
        )
        embed.set_image(queued.player.thumbnail_url)

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
        return
    if immutable:
        return message.channel.id == message.guild.voice_client.channel.id
    else:
        if not message.author.voice:
            return False
        return message.author.voice.channel.id == message.guild.voice_client.channel.id
