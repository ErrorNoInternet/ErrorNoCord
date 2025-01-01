import disnake

import constants


def format_duration(duration: int):
    format_plural = lambda noun, count: noun if count == 1 else noun + "s"
    segments = []

    weeks, duration = divmod(duration, 604800)
    if weeks > 0:
        segments.append(f"{weeks} {format_plural('week', weeks)}")

    days, duration = divmod(duration, 86400)
    if days > 0:
        segments.append(f"{days} {format_plural('day', days)}")

    hours, duration = divmod(duration, 3600)
    if hours > 0:
        segments.append(f"{hours} {format_plural('hour', hours)}")

    minutes, duration = divmod(duration, 60)
    if minutes > 0:
        segments.append(f"{minutes} {format_plural('minute', minutes)}")

    if duration > 0:
        segments.append(f"{duration} {format_plural('second', duration)}")

    return ", ".join(segments)


async def add_check_reaction(message):
    await message.add_reaction("✅")


async def reply(message, *args):
    await message.reply(*args, allowed_mentions=disnake.AllowedMentions.none())


async def invalid_user_handler(interaction):
    await interaction.response.send_message(
        "You are not the intended receiver of this message!", ephemeral=True
    )


def filter_secrets(text: str) -> str:
    for secret_name, secret in constants.SECRETS.items():
        if not secret:
            continue
        text = text.replace(secret, f"<{secret_name}>")
    return text
