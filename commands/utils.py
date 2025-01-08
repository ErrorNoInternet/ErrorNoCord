from enum import Enum

import constants


class Command(Enum):
    CLEAR = "clear"
    CURRENT = "current"
    EXECUTE = "execute"
    FAST_FORWARD = "ff"
    HELP = "help"
    JOIN = "join"
    LEAVE = "leave"
    PAUSE = "pause"
    PLAY = "play"
    PLAYING = "playing"
    PURGE = "purge"
    QUEUE = "queue"
    RELOAD = "reload"
    RESUME = "resume"
    SKIP = "skip"
    UPTIME = "uptime"
    VOLUME = "volume"


def match_token(token: str) -> list[Command]:
    if token.lower() == "r":
        return [Command.RELOAD]

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


def match(command: str) -> list[Command] | None:
    if tokens := tokenize(command):
        return match_token(tokens[0])


def tokenize(string: str) -> list[str]:
    tokens = []
    token = ""
    in_quotes = False
    quote_char = None
    escape = False

    for char in string[len(constants.PREFIX) :]:
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
