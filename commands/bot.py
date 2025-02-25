import os
import threading
import time

import disnake
import psutil
from yt_dlp import version

import arguments
import commands
from constants import EMBED_COLOR
from state import client, start_time
from utils import format_duration, reply, surround


async def status(message):
    member_count = 0
    channel_count = 0
    for guild in client.guilds:
        member_count += len(guild.members)
        channel_count += len(guild.channels)
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1048576

    embed = disnake.Embed(color=EMBED_COLOR)
    embed.add_field(
        name="Latency",
        value=surround(f"{round(client.latency * 1000, 1)} ms"),
    )
    embed.add_field(
        name="Memory",
        value=surround(f"{round(memory_usage, 1)} MiB"),
    )
    embed.add_field(
        name="Threads",
        value=surround(threading.active_count()),
    )
    embed.add_field(
        name="Guilds",
        value=surround(len(client.guilds)),
    )
    embed.add_field(
        name="Members",
        value=surround(member_count),
    )
    embed.add_field(
        name="Channels",
        value=surround(channel_count),
    )
    embed.add_field(
        name="Disnake",
        value=surround(disnake.__version__),
    )
    embed.add_field(
        name="yt-dlp",
        value=surround(version.__version__),
    )
    embed.add_field(
        name="Uptime",
        value=surround(format_duration(int(time.time() - start_time), short=True)),
    )
    await reply(message, embed=embed)


async def uptime(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0],
        "print bot uptime",
    )
    parser.add_argument(
        "-s",
        "--since",
        action="store_true",
        help="bot up since",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if args.since:
        await reply(message, f"{round(start_time)}")
    else:
        await reply(message, f"up {format_duration(int(time.time() - start_time))}")


async def ping(message):
    await reply(
        message,
        embed=disnake.Embed(
            title="Pong :ping_pong:",
            description=f"Latency: **{round(client.latency * 1000, 1)} ms**",
            color=EMBED_COLOR,
        ),
    )


async def help(message):
    await reply(
        message,
        ", ".join(
            [f"`{command.value}`" for command in commands.Command.__members__.values()]
        ),
    )
