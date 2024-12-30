import enum

import constants


class Command(enum.Enum):
    CLEAR = "clear"
    EXECUTE = "execute"
    JOIN = "join"
    LEAVE = "leave"
    PAUSE = "pause"
    PLAY = "play"
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

    return list(
        filter(
            lambda command: command.value.startswith(token.lower()),
            Command.__members__.values(),
        )
    )


def match(command: str) -> None | list[Command]:
    if tokens := tokenize(command):
        return match_token(tokens[0])


def tokenize(string: str) -> list[str]:
    tokens = []
    current_token = []
    in_quotes = False
    escape_next = False

    for char in string[len(constants.PREFIX) :]:
        if escape_next:
            current_token.append(char)
            escape_next = False
        elif char == "\\":
            escape_next = True
        elif char in ['"', "'"]:
            if in_quotes:
                if current_token and current_token[0] == char:
                    in_quotes = False
            else:
                in_quotes = True
        elif char.isspace() and not in_quotes:
            if current_token:
                tokens.append("".join(current_token))
                current_token = []
        else:
            current_token.append(char)

    if current_token:
        tokens.append("".join(current_token))

    return tokens
