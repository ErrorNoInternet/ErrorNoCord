import disnake

import constants


async def reply(message, *args):
    await message.reply(*args, allowed_mentions=disnake.AllowedMentions.none())


async def invalid_user_handler(interaction):
    await interaction.response.send_message(
        "You are not the intended receiver of this message!", ephemeral=True
    )


def filter_secrets(text: str) -> str:
    for secret_name, secret in constants.secrets.items():
        if not secret:
            continue
        text = text.replace(secret, f"<{secret_name}>")
    return text
