import contextlib
import importlib
import inspect
import io
import textwrap
import traceback

import disnake_paginator

import commands
import constants
import utils
from state import reloaded_modules


async def on_message(message):
    tokens = commands.tokenize(message.content)
    if not tokens:
        return
    matched = commands.match_token(tokens[0])
    if not matched:
        return

    if len(matched) > 1:
        await message.reply(
            f"ambiguous command, could be {' or '.join([f'`{match.value}`' for match in matched])}",
            mention_author=False,
        )
        return

    C = commands.Command
    try:
        match matched[0]:
            case C.EXECUTE if message.author.id in constants.OWNERS:
                code = message.content[len(tokens[0]) + 1 :].strip().strip("`")
                for replacement in ["python", "py"]:
                    if code.startswith(replacement):
                        code = code[len(replacement) :]

                stdout = io.StringIO()
                try:
                    with contextlib.redirect_stdout(stdout):
                        if "#globals" in code:
                            exec(
                                f"async def run_code():\n{textwrap.indent(code, '   ')}",
                                globals(),
                            )
                            await globals()["run_code"]()
                        else:
                            dictionary = dict(locals(), **globals())
                            exec(
                                f"async def run_code():\n{textwrap.indent(code, '   ')}",
                                dictionary,
                                dictionary,
                            )
                            await dictionary["run_code"]()
                        output = stdout.getvalue()
                except Exception as e:
                    output = "`" + str(e) + "`"

                output = utils.filter_secrets(output)

                if len(output) > 2000:
                    output = output.replace("`", "\\`")
                    pager = disnake_paginator.ButtonPaginator(
                        prefix=f"```\n",
                        suffix="```",
                        color=constants.EMBED_COLOR,
                        segments=disnake_paginator.split(output),
                        invalid_user_function=utils.invalid_user_handler,
                    )
                    await pager.start(
                        disnake_paginator.wrappers.MessageInteractionWrapper(message)
                    )
                elif len(output.strip()) == 0:
                    await message.add_reaction("✅")
                else:
                    await message.channel.send(output)
            case C.CLEAR | C.PURGE:
                await commands.tools.clear(message)
            case C.JOIN:
                await commands.voice.join(message)
            case C.LEAVE:
                await commands.voice.leave(message)
            case C.QUEUE | C.PLAY:
                await commands.voice.queue_or_play(message)
            case C.SKIP:
                await commands.voice.skip(message)
            case C.RESUME:
                await commands.voice.resume(message)
            case C.PAUSE:
                await commands.voice.pause(message)
            case C.VOLUME:
                await commands.voice.volume(message)
    except Exception as e:
        await message.reply(
            f"exception occurred while processing command: ```\n{''.join(traceback.format_exception(e)).replace('`', '\\`')}```",
            mention_author=False,
        )


def __reload_module__():
    for name, module in globals().items():
        if (
            inspect.ismodule(module)
            and name not in constants.RELOAD_BLACKLISTED_MODULES
        ):
            importlib.reload(module)
            if "__reload_module__" in dir(module) and name not in reloaded_modules:
                reloaded_modules.add(name)
                module.__reload_module__()
