import argparse
import contextlib
import io

import utils


class ArgumentParser:
    def __init__(self, command, description):
        self.parser = argparse.ArgumentParser(
            command, description=description, exit_on_error=False
        )

    def print_help(self):
        help_buffer = io.StringIO()
        with contextlib.redirect_stdout(help_buffer):
            self.parser.print_help()
        return help_buffer.getvalue().replace(" and exit", "")

    def add_mutually_exclusive_group(self, *args, **kwargs):
        return self.parser.add_mutually_exclusive_group(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        return self.parser.add_argument(*args, **kwargs)

    async def parse_args(self, message, tokens) -> argparse.Namespace | None:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                args = self.parser.parse_args(tokens[1:])
            return args
        except SystemExit:
            await utils.reply(message, f"```\n{self.print_help()}```")
        except Exception as e:
            await utils.reply(message, f"`{e}`")


def range_type(string, min=0, max=100):
    try:
        value = int(string)
    except ValueError:
        raise argparse.ArgumentTypeError(f"value not a valid integer")

    if min <= value <= max:
        return value
    else:
        raise argparse.ArgumentTypeError(f"value not in range {min}-{max}")
