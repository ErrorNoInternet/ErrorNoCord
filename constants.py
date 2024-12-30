import os

EMBED_COLOR = 0xFF6600
OWNERS = [531392146767347712]
PREFIX = "%"

ytdl_format_options = {
    "default_search": "auto",
    "format": "bestaudio/best",
    "ignoreerrors": False,
    "logtostderr": False,
    "no_warnings": True,
    "noplaylist": True,
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "quiet": True,
    "restrictfilenames": True,
    "socket_timeout": 10,
    "source_address": "0.0.0.0",
}


secrets = {
    "TOKEN": os.getenv("BOT_TOKEN"),
}
