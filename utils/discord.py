import os
import time
from logging import error, info

import disnake

import commands
from state import command_cooldowns, message_responses


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


async def reply(message, *args, **kwargs):
    if message.id in message_responses:
        if len(args) == 0:
            kwargs["content"] = None
        elif len(kwargs) == 0:
            kwargs["embeds"] = []

        try:
            await message_responses[message.id].edit(
                *args, **kwargs, allowed_mentions=disnake.AllowedMentions.none()
            )
            return
        except Exception:
            pass

    try:
        response = await message.reply(
            *args, **kwargs, allowed_mentions=disnake.AllowedMentions.none()
        )
    except Exception:
        response = await channel_send(message, *args, **kwargs)
    message_responses[message.id] = response
    return message_responses[message.id]


async def channel_send(message, *args, **kwargs):
    await message.channel.send(
        *args, **kwargs, allowed_mentions=disnake.AllowedMentions.none()
    )


def load_opus():
    for path in filter(
        lambda p: os.path.exists(p),
        ["/usr/lib64/libopus.so.0", "/usr/lib/libopus.so.0"],
    ):
        try:
            disnake.opus.load_opus(path)
            info(f"successfully loaded opus from {path}")
            return
        except Exception as e:
            error(f"failed to load opus from {path}: {e}")
    raise Exception("could not locate working opus library")


def snowflake_timestamp(id):
    return round(((id >> 22) + 1420070400000) / 1000)


async def add_check_reaction(message):
    await message.add_reaction("✅")


async def invalid_user_handler(interaction):
    await interaction.response.send_message(
        "you are not the intended receiver of this message!", ephemeral=True
    )


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
