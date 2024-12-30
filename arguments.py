import argparse
import contextlib
import io


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

    def add_argument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    async def parse_args(self, message, tokens) -> argparse.Namespace | None:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                args = self.parser.parse_args(tokens[1:])
            return args
        except SystemExit:
            await message.reply(f"```\n{self.print_help()}```", mention_author=False)
        except Exception as e:
            await message.reply(f"`{e}`", mention_author=False)
