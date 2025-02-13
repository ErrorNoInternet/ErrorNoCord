from enum import Enum
from functools import lru_cache

import constants


class Command(Enum):
    CLEAR = "clear"
    CURRENT = "current"
    EXECUTE = "execute"
    FAST_FORWARD = "ff"
    HELP = "help"
    JOIN = "join"
    LEAVE = "leave"
    LOOKUP = "lookup"
    PAUSE = "pause"
    PING = "ping"
    PLAY = "play"
    PLAYING = "playing"
    PURGE = "purge"
    QUEUE = "queue"
    RELOAD = "reload"
    RESUME = "resume"
    SKIP = "skip"
    SPONSORBLOCK = "sponsorblock"
    STATUS = "status"
    UPTIME = "uptime"
    VOLUME = "volume"


@lru_cache
def match_token(token: str) -> list[Command]:
    match token.lower():
        case "r":
            return [Command.RELOAD]
        case "s":
            return [Command.SKIP]
        case "c":
            return [Command.CURRENT]

    if exact_match := list(
        filter(
            lambda command: command.value == token.lower(),
            Command.__members__.values(),
        )
    ):
        return exact_match

    return list(
        filter(
            lambda command: command.value.startswith(token.lower()),
            Command.__members__.values(),
        )
    )


@lru_cache
def match(command: str) -> list[Command] | None:
    if tokens := tokenize(command):
        return match_token(tokens[0])


@lru_cache
def tokenize(string: str, remove_prefix: bool = True) -> list[str]:
    tokens = []
    token = ""
    in_quotes = False
    quote_char = None
    escape = False

    if remove_prefix:
        string = string[len(constants.PREFIX) :]

    for char in string:
        if escape:
            token += char
            escape = False
        elif char == "\\":
            escape = True
        elif char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
        elif char.isspace() and not in_quotes:
            if token:
                tokens.append(token)
                token = ""
        else:
            token += char

    if token:
        tokens.append(token)
    return tokens
