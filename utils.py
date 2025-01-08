import os
import time
from logging import error, info, warning

import disnake

import commands
import constants
from state import command_cooldowns, message_responses


class ChannelResponseWrapper:
    def __init__(self, message):
        self.message = message
        self.sent_message = None

    async def send_message(self, **kwargs):
        if "ephemeral" in kwargs:
            del kwargs["ephemeral"]
        self.sent_message = await reply(self.message, **kwargs)

    async def edit_message(self, content=None, embed=None, view=None):
        if self.sent_message:
            content = content or self.sent_message.content
            if not embed and len(self.sent_message.embeds) > 0:
                embed = self.sent_message.embeds[0]
            await self.sent_message.edit(content=content, embed=embed, view=view)


class MessageInteractionWrapper:
    def __init__(self, message):
        self.message = message
        self.author = message.author
        self.response = ChannelResponseWrapper(message)

    async def edit_original_message(self, content=None, embed=None, view=None):
        await self.response.edit_message(content=content, embed=embed, view=view)


def cooldown(message, cooldown_time: int):
    possible_commands = commands.match(message.content)
    if not possible_commands or len(possible_commands) > 1:
        return
    command = possible_commands[0]

    end_time = time.time() + cooldown_time
    if message.author.id in command_cooldowns:
        command_cooldowns[message.author.id][command] = end_time
    else:
        command_cooldowns[message.author.id] = {command: end_time}


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


def parse_snowflake(id):
    return round(((id >> 22) + 1420070400000) / 1000)


async def add_check_reaction(message):
    await message.add_reaction("✅")


async def reply(message, *args, **kwargs):
    if message.id in message_responses:
        await message_responses[message.id].edit(
            *args, **kwargs, allowed_mentions=disnake.AllowedMentions.none()
        )
    else:
        response = await message.reply(
            *args, **kwargs, allowed_mentions=disnake.AllowedMentions.none()
        )
        message_responses[message.id] = response
    return message_responses[message.id]


async def channel_send(message, *args, **kwargs):
    await message.channel.send(
        *args, **kwargs, allowed_mentions=disnake.AllowedMentions.none()
    )


async def invalid_user_handler(interaction):
    await interaction.response.send_message(
        "you are not the intended receiver of this message!", ephemeral=True
    )


def filter_secrets(text: str, secrets=constants.SECRETS) -> str:
    for secret_name, secret in secrets.items():
        if not secret:
            continue
        text = text.replace(secret, f"<{secret_name}>")
    return text


def load_opus():
    warning("opus wasn't automatically loaded! trying to load manually...")
    for path in ["/usr/lib64/libopus.so.0", "/usr/lib/libopus.so.0"]:
        if os.path.exists(path):
            try:
                disnake.opus.load_opus(path)
                info(f"successfully loaded opus from {path}")
                return
            except Exception as e:
                error(f"failed to load opus from {path}: {e}")
    raise Exception("could not locate working opus library")
