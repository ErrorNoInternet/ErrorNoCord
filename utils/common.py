from collections import OrderedDict

from constants import SECRETS


def surround(inner, outer="```"):
    return outer + str(inner) + outer


def format_duration(duration: int, natural: bool = False, short: bool = False):
    def format_plural(noun, count):
        if short:
            return noun[0]
        return " " + (noun if count == 1 else noun + "s")

    segments = []

    weeks, duration = divmod(duration, 604800)
    if weeks > 0:
        segments.append(f"{weeks}{format_plural('week', weeks)}")

    days, duration = divmod(duration, 86400)
    if days > 0:
        segments.append(f"{days}{format_plural('day', days)}")

    hours, duration = divmod(duration, 3600)
    if hours > 0:
        segments.append(f"{hours}{format_plural('hour', hours)}")

    minutes, duration = divmod(duration, 60)
    if minutes > 0:
        segments.append(f"{minutes}{format_plural('minute', minutes)}")

    if duration > 0:
        segments.append(f"{duration}{format_plural('second', duration)}")

    separator = " " if short else ", "
    if not natural or len(segments) <= 1:
        return separator.join(segments)
    return separator.join(segments[:-1]) + f" and {segments[-1]}"


def filter_secrets(text: str, secrets=SECRETS) -> str:
    for secret_name, secret in secrets.items():
        if not secret:
            continue
        text = text.replace(secret, f"<{secret_name}>")
    return text


class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        self.size_limit = kwargs.pop("size_limit", 1000)
        super().__init__(*args, **kwargs)
        self._check_size_limit()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)
