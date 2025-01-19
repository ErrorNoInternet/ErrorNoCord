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

BAR_LENGTH = 35
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
    "commands.voice.channel",
    "commands.voice.playback",
    "commands.voice.playing",
    "commands.voice.queue",
    "commands.voice.utils",
    "constants",
    "core",
    "events",
    "extra",
    "fun",
    "tasks",
    "utils",
    "voice",
    "youtubedl",
    "yt_dlp",
    "yt_dlp.version",
]
PUBLIC_FLAGS = {
    1: "Discord Employee",
    2: "Discord Partner",
    4: "HypeSquad Events",
    8: "Bug Hunter Level 1",
    64: "HypeSquad Bravery",
    128: "HypeSquad Brilliance",
    256: "HypeSquad Balance",
    512: "Early Supporter",
    1024: "Team User",
    16384: "Bug Hunter Level 2",
    65536: "Verified Bot",
    131072: "Verified Bot Developer",
    262144: "Discord Certified Moderator",
    524288: "HTTP Interactions Only",
    4194304: "Active Developer",
}
BADGE_EMOJIS = {
    "Discord Employee": "<:DiscordStaff:879666899980546068>",
    "Discord Partner": "<:DiscordPartner:879668340434534400>",
    "HypeSquad Events": "<:HypeSquadEvents:879666970310606848>",
    "Bug Hunter Level 1": "<:BugHunter1:879666851448234014>",
    "HypeSquad Bravery": "<:HypeSquadBravery:879666945153175612>",
    "HypeSquad Brilliance": "<:HypeSquadBrilliance:879666956884643861>",
    "HypeSquad Balance": "<:HypeSquadBalance:879666934717771786>",
    "Early Supporter": "<:EarlySupporter:879666916493496400>",
    "Team User": "<:TeamUser:890866907996127305>",
    "Bug Hunter Level 2": "<:BugHunter2:879666866971357224>",
    "Verified Bot": "<:VerifiedBot:879670687554498591>",
    "Verified Bot Developer": "<:VerifiedBotDeveloper:879669786550890507>",
    "Discord Certified Moderator": "<:DiscordModerator:879666882976837654>",
    "HTTP Interactions Only": "<:HTTPInteractionsOnly:1047141867806015559>",
    "Active Developer": "<:ActiveDeveloper:1047141451244523592>",
}
APPLICATION_FLAGS = {
    1 << 12: "Presence Intent",
    1 << 13: "Presence Intent (unverified)",
    1 << 14: "Guild Members Intent",
    1 << 15: "Guild Members Intent (unverified)",
    1 << 16: "Unusual Growth (verification suspended)",
    1 << 18: "Message Content Intent",
    1 << 19: "Message Content Intent (unverified)",
    1 << 23: "Suports Application Commands",
}

SECRETS = {
    "TOKEN": os.getenv("BOT_TOKEN"),
}
