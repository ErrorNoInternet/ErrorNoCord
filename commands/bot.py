import os
import threading
import time

import disnake
import psutil
from yt_dlp import version

import arguments
import commands
import utils
from constants import EMBED_COLOR
from state import client, start_time


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
        value=f"```{round(client.latency * 1000, 1)} ms```",
    )
    embed.add_field(
        name="Memory",
        value=f"```{round(memory_usage, 1)} MiB```",
    )
    embed.add_field(
        name="Threads",
        value=f"```{threading.active_count()}```",
    )
    embed.add_field(
        name="Guilds",
        value=f"```{len(client.guilds)}```",
    )
    embed.add_field(
        name="Members",
        value=f"```{member_count}```",
    )
    embed.add_field(
        name="Channels",
        value=f"```{channel_count}```",
    )
    embed.add_field(
        name="Disnake",
        value=f"```{disnake.__version__}```",
    )
    embed.add_field(
        name="yt-dlp",
        value=f"```{version.__version__}```",
    )
    embed.add_field(
        name="Uptime",
        value=f"```{utils.format_duration(int(time.time() - start_time), short=True)}```",
    )
    await utils.reply(message, embed=embed)


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
        await utils.reply(message, f"{round(start_time)}")
    else:
        await utils.reply(
            message, f"up {utils.format_duration(int(time.time() - start_time))}"
        )


async def ping(message):
    await utils.reply(
        message,
        embed=disnake.Embed(
            title="Pong :ping_pong:",
            description=f"Latency: **{round(client.latency * 1000, 1)} ms**",
            color=EMBED_COLOR,
        ),
    )


async def help(message):
    await utils.reply(
        message,
        ", ".join(
            [f"`{command.value}`" for command in commands.Command.__members__.values()]
        ),
    )
