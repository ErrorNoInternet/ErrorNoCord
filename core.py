import asyncio
import contextlib
import importlib
import inspect
import io
import textwrap
import traceback

import disnake_paginator

import commands
import constants
import core
import utils
from state import client, command_locks, executed_messages


async def on_message(message, edited=False):
    if not message.content.startswith(constants.PREFIX) or message.author.bot:
        return

    tokens = commands.tokenize(message.content)
    if not tokens:
        return
    matched = commands.match_token(tokens[0])
    if not matched:
        return

    if len(matched) > 1:
        await utils.reply(
            message,
            f"ambiguous command, could be {' or '.join([f'`{match.value}`' for match in matched])}",
        )
        return

    if message.guild.id not in command_locks:
        command_locks[message.guild.id] = asyncio.Lock()

    C = commands.Command
    try:
        match matched[0]:
            case C.RELOAD if message.author.id in constants.OWNERS:
                reloaded_modules = set()
                for module in filter(
                    lambda v: inspect.ismodule(v)
                    and v.__name__ in constants.RELOADABLE_MODULES,
                    globals().values(),
                ):
                    core.rreload(reloaded_modules, module)

                await utils.add_check_reaction(message)
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
                    await disnake_paginator.ButtonPaginator(
                        prefix=f"```\n",
                        suffix="```",
                        invalid_user_function=utils.invalid_user_handler,
                        color=constants.EMBED_COLOR,
                        segments=disnake_paginator.split(output),
                    ).start(
                        disnake_paginator.wrappers.MessageInteractionWrapper(message)
                    )
                elif len(output.strip()) == 0:
                    await utils.add_check_reaction(message)
                else:
                    if message.id in executed_messages:
                        await executed_messages[message.id].edit(output)
                    else:
                        response = await message.channel.send(output)
                        executed_messages[message.id] = response
            case C.CLEAR | C.PURGE if message.author.id in constants.OWNERS:
                await commands.tools.clear(message)
            case C.JOIN:
                await commands.voice.join(message)
            case C.LEAVE:
                await commands.voice.leave(message)
            case C.QUEUE | C.PLAY:
                async with command_locks[message.guild.id]:
                    await commands.voice.queue_or_play(message, edited)
            case C.SKIP:
                async with command_locks[message.guild.id]:
                    await commands.voice.skip(message)
            case C.RESUME:
                await commands.voice.resume(message)
            case C.PAUSE:
                await commands.voice.pause(message)
            case C.VOLUME:
                await commands.voice.volume(message)
            case C.HELP:
                await commands.bot.help(message)
            case C.UPTIME:
                await commands.bot.uptime(message)
            case C.PLAYING:
                await commands.voice.playing(message)
    except Exception as e:
        await utils.reply(
            message,
            f"exception occurred while processing command: ```\n{''.join(traceback.format_exception(e)).replace('`', '\\`')}```",
        )


async def on_voice_state_update(_, before, after):
    is_empty = lambda channel: [m.id for m in (channel.members if channel else [])] == [
        client.user.id
    ]
    c = None
    if is_empty(before.channel):
        c = before.channel
    elif is_empty(after.channel):
        c = after.channel
    if c:
        await c.guild.voice_client.disconnect()


def rreload(reloaded_modules, module):
    reloaded_modules.add(module.__name__)

    for submodule in filter(
        lambda v: inspect.ismodule(v)
        and v.__name__ in constants.RELOADABLE_MODULES
        and v.__name__ not in reloaded_modules,
        vars(module).values(),
    ):
        rreload(reloaded_modules, submodule)

    importlib.reload(module)

    if "__reload_module__" in dir(module):
        module.__reload_module__()
