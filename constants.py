import os

YTDL_OPTIONS = {
    "color": "never",
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
    "extra",
    "tasks",
    "utils",
    "voice",
    "youtubedl",
]

SECRETS = {
    "TOKEN": os.getenv("BOT_TOKEN"),
}
