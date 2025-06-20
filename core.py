import asyncio
import contextlib
import importlib
import inspect
import io
import signal
import textwrap
import time
import traceback
from logging import debug

import disnake
import disnake_paginator

import commands
import utils
from commands import Command as C
from constants import EMBED_COLOR, OWNERS, PREFIX, RELOADABLE_MODULES
from state import client, command_cooldowns, command_locks, idle_tracker


async def on_message(message, edited=False):
    if not message.content.startswith(PREFIX) or message.author.bot:
        return

    tokens = commands.tokenize(message.content)
    if not tokens:
        return
    matched = commands.match_token(tokens[0])
    if not matched:
        return

    idle_tracker["last_used"] = time.time()
    if idle_tracker["is_idle"]:
        idle_tracker["is_idle"] = False
        await client.change_presence(status=disnake.Status.online)

    if len(matched) > 1:
        await utils.reply(
            message,
            f"ambiguous command, could be {' or '.join([f'`{match.value}`' for match in matched])}",
        )
        return
    matched = matched[0]

    if (message.guild.id, message.author.id) not in command_locks:
        command_locks[(message.guild.id, message.author.id)] = asyncio.Lock()
    await command_locks[(message.guild.id, message.author.id)].acquire()

    try:
        if (cooldowns := command_cooldowns.get(message.author.id)) and not edited:
            if (end_time := cooldowns.get(matched)) and (
                remaining_time := round(end_time - time.time()) > 0
            ):
                await utils.reply(
                    message,
                    f"please wait **{utils.format_duration(remaining_time, natural=True)}** before using this command again!",
                )
                return

        match matched:
            case C.RELOAD if message.author.id in OWNERS:
                start = time.time()
                reloaded_modules = reload()
                end = time.time()
                debug(
                    f"reloaded {len(reloaded_modules)} modules in {round(end - start, 2)}s",
                )

                await utils.add_check_reaction(message)

            case C.EXECUTE if message.author.id in OWNERS:
                code = message.content[len(tokens[0]) + 1 :].strip().strip("`")
                for replacement in ["python", "py"]:
                    if code.startswith(replacement):
                        code = code[len(replacement) :]

                try:
                    stdout = io.StringIO()
                    with contextlib.redirect_stdout(stdout):
                        wrapped_code = (
                            f"async def run_code():\n{textwrap.indent(code, '   ')}"
                        )
                        if "# globals" in code:
                            exec(wrapped_code, globals())
                            await globals()["run_code"]()
                        else:
                            dictionary = dict(locals(), **globals())
                            exec(wrapped_code, dictionary, dictionary)
                            await dictionary["run_code"]()
                        output = stdout.getvalue()
                except Exception as e:
                    output = "`" + str(e) + "`"
                output = utils.filter_secrets(output)

                if len(output) > 2000:
                    output = output.replace("`", "\\`")
                    await disnake_paginator.ButtonPaginator(
                        prefix="```\n",
                        suffix="```",
                        invalid_user_function=utils.invalid_user_handler,
                        color=EMBED_COLOR,
                        segments=disnake_paginator.split(output),
                    ).start(utils.MessageInteractionWrapper(message))
                elif len(output.strip()) == 0:
                    await utils.add_check_reaction(message)
                else:
                    await utils.reply(message, output)

            case C.CLEAR | C.PURGE if message.author.id in OWNERS:
                await commands.tools.clear(message)
            case C.JOIN:
                await commands.voice.join(message)
            case C.LEAVE:
                await commands.voice.leave(message)
            case C.QUEUE | C.PLAY:
                await commands.voice.queue_or_play(message, edited)
            case C.SKIP:
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
            case C.PLAYING | C.CURRENT:
                await commands.voice.playing(message)
            case C.FAST_FORWARD:
                await commands.voice.fast_forward(message)
            case C.STATUS:
                await commands.bot.status(message)
            case C.PING:
                await commands.bot.ping(message)
            case C.LOOKUP:
                await commands.tools.lookup(message)
            case C.SPONSORBLOCK:
                await commands.voice.sponsorblock_command(message)
    except Exception as e:
        await utils.reply(
            message,
            f"exception occurred while processing command: ```\n{''.join(traceback.format_exception(e)).replace('`', '\\`')}```",
        )
        raise e
    finally:
        command_locks[(message.guild.id, message.author.id)].release()


async def on_voice_state_update(_, before, after):
    def is_empty(channel):
        return [m.id for m in (channel.members if channel else [])] == [client.user.id]

    channel = None
    if is_empty(before.channel):
        channel = before.channel
    elif is_empty(after.channel):
        channel = after.channel

    if channel:
        await channel.guild.voice_client.disconnect()


def rreload(reloaded_modules, module):
    reloaded_modules.add(module.__name__)

    for submodule in filter(
        lambda sm: inspect.ismodule(sm)
        and sm.__name__ in RELOADABLE_MODULES
        and sm.__name__ not in reloaded_modules,
        vars(module).values(),
    ):
        rreload(reloaded_modules, submodule)

    importlib.reload(module)

    if "__reload_module__" in dir(module):
        module.__reload_module__()


def reload(*_):
    reloaded_modules = set()
    rreload(reloaded_modules, __import__("core"))
    rreload(reloaded_modules, __import__("extra"))
    for module in filter(
        lambda v: inspect.ismodule(v) and v.__name__ in RELOADABLE_MODULES,
        globals().values(),
    ):
        rreload(reloaded_modules, module)
    return reloaded_modules


signal.signal(signal.SIGUSR1, reload)
