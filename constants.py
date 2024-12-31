import os

EMBED_COLOR = 0xFF6600
OWNERS = [531392146767347712]
PREFIX = "%"
RELOADABLE_MODULES = [
    "arguments",
    "commands",
    "commands.bot",
    "commands.tools",
    "commands.utils",
    "commands.voice",
    "constants",
    "core",
    "events",
    "utils",
    "voice",
    "youtubedl",
]

YTDL_OPTIONS = {
    "default_search": "auto",
    "format": "bestaudio/best",
    "ignoreerrors": False,
    "logtostderr": False,
    "no_warnings": True,
    "noplaylist": True,
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "quiet": True,
    "restrictfilenames": True,
    "socket_timeout": 15,
    "source_address": "0.0.0.0",
}


SECRETS = {
    "TOKEN": os.getenv("BOT_TOKEN"),
}
