import re

import disnake
import requests

import arguments
import commands
import utils
from constants import APPLICATION_FLAGS, BADGE_EMOJIS, EMBED_COLOR, PUBLIC_FLAGS
from state import client


async def lookup(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0],
        "look up a user or application on discord by their ID",
    )
    parser.add_argument(
        "-a",
        "--application",
        action="store_true",
        help="search for applications instead of users",
    )
    parser.add_argument(
        "id",
        type=int,
        help="the ID to perform a search for",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if args.application:
        response = requests.get(
            f"https://discord.com/api/v9/applications/{args.id}/rpc"
        ).json()
        if "code" in response.keys():
            await utils.reply(message, "application not found!")
            return

        embed = disnake.Embed(description=response["description"], color=EMBED_COLOR)
        embed.set_thumbnail(
            url=f"https://cdn.discordapp.com/app-icons/{response['id']}/{response['icon']}.webp"
        )
        embed.add_field(name="Application Name", value=response["name"])
        embed.add_field(name="Application ID", value="`" + response["id"] + "`")
        embed.add_field(
            name="Public Bot",
            value=f"{'`'+str(response['bot_public'])+'`' if 'bot_public' in response.keys() != None else 'No bot'}",
        )
        embed.add_field(name="Public Flags", value="`" + str(response["flags"]) + "`")
        embed.add_field(
            name="Terms of Service",
            value=(
                "None"
                if "terms_of_service_url" not in response.keys()
                else f"[Link]({response['terms_of_service_url']})"
            ),
        )
        embed.add_field(
            name="Privacy Policy",
            value=(
                "None"
                if "privacy_policy_url" not in response.keys()
                else f"[Link]({response['privacy_policy_url']})"
            ),
        )
        embed.add_field(
            name="Creation Time",
            value=f"<t:{utils.parse_snowflake(int(response['id']))}:R>",
        )
        embed.add_field(
            name="Default Invite URL",
            value=(
                "None"
                if "install_params" not in response.keys()
                else f"[Link](https://discord.com/oauth2/authorize?client_id={response['id']}&permissions={response['install_params']['permissions']}&scope={'%20'.join(response['install_params']['scopes'])})"
            ),
        )
        embed.add_field(
            name="Custom Invite URL",
            value=(
                "None"
                if "custom_install_url" not in response.keys()
                else f"[Link]({response['custom_install_url']})"
            ),
        )

        bot_intents = []
        for application_flag, intent_name in APPLICATION_FLAGS.items():
            if response["flags"] & application_flag == application_flag:
                if intent_name.replace(" (unverified)", "") not in bot_intents:
                    bot_intents.append(intent_name)
        embed.add_field(
            name="Application Flags",
            value=", ".join(bot_intents) if bot_intents else "None",
        )

        bot_tags = ""
        if "tags" in response.keys():
            for tag in response["tags"]:
                bot_tags += tag + ", "
        embed.add_field(
            name="Tags", value="None" if bot_tags == "" else bot_tags[:-2], inline=False
        )
    else:
        try:
            user = await client.fetch_user(args.id)
        except Exception:
            await utils.reply(message, "user not found!")
            return

        badges = ""
        for flag, flag_name in PUBLIC_FLAGS.items():
            if user.public_flags.value & flag == flag:
                if flag_name != "None":
                    try:
                        badges += BADGE_EMOJIS[PUBLIC_FLAGS[flag]]
                    except:
                        raise Exception(f"unable to find badge: {PUBLIC_FLAGS[flag]}")

        accent_color = 0x000000
        user_object = await client.fetch_user(user.id)
        if user_object.accent_color != None:
            accent_color = user_object.accent_color

        embed = disnake.Embed(color=accent_color)
        embed.add_field(
            name="User ID",
            value=f"`{user.id}`",
        )
        embed.add_field(
            name="Discriminator",
            value=f"`{user.name}#{user.discriminator}`",
        )
        embed.add_field(
            name="Creation Time",
            value=f"<t:{utils.parse_snowflake(int(user.id))}:R>",
        )
        embed.add_field(
            name="Public Flags",
            value=f"`{user.public_flags.value}` {badges}",
        )
        embed.add_field(
            name="Bot User",
            value=f"`{user.bot}`",
        )
        embed.add_field(
            name="System User",
            value=f"`{user.system}`",
        )
        embed.set_thumbnail(url=user.avatar if user.avatar else user.default_avatar)
        if user_object.banner:
            embed.set_image(url=user_object.banner)

    await utils.reply(message, embed=embed)


async def clear(message):
    tokens = commands.tokenize(message.content)
    parser = arguments.ArgumentParser(
        tokens[0],
        "bulk delete messages in the current channel matching certain criteria",
    )
    parser.add_argument(
        "count",
        type=lambda c: arguments.range_type(c, min=1, max=1000),
        help="amount of messages to delete",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-r",
        "--regex",
        required=False,
        help="delete messages with content matching this regex",
    )
    group.add_argument(
        "-c",
        "--contains",
        required=False,
        help="delete messages with content containing this substring",
    )
    parser.add_argument(
        "-i",
        "--case-insensitive",
        action="store_true",
        help="ignore case sensitivity when deleting messages",
    )
    parser.add_argument(
        "-a",
        "--author-id",
        type=int,
        action="append",
        help="delete messages whose author matches this id",
    )
    parser.add_argument(
        "-o",
        "--oldest-first",
        action="store_true",
        help="delete oldest messages first",
    )
    parser.add_argument(
        "-R",
        "--reactions",
        action="store_true",
        help="delete messages with reactions",
    )
    parser.add_argument(
        "-A",
        "--attachments",
        action="store_true",
        help="delete messages with attachments",
    )
    parser.add_argument(
        "-d",
        "--delete-command",
        action="store_true",
        help="delete the command message as well",
    )
    parser.add_argument(
        "-I",
        "--ignore-ids",
        type=int,
        action="append",
        help="ignore messages with this id",
    )
    if not (args := await parser.parse_args(message, tokens)):
        return

    if args.delete_command:
        try:
            await message.delete()
        except Exception:
            pass

    regex = None
    if r := args.regex:
        regex = re.compile(r, re.IGNORECASE if args.case_insensitive else 0)

    def check(m):
        if (ids := args.ignore_ids) and m.id in ids:
            return False
        c = []
        if regex:
            c.append(regex.search(m.content))
        if s := args.contains:
            if args.case_insensitive:
                c.append(s.lower() in m.content.lower())
            else:
                c.append(s in m.content)
        if i := args.author_id:
            c.append(m.author.id in i)
        if args.reactions:
            c.append(len(m.reactions) > 0)
        if args.attachments:
            c.append(len(m.attachments) > 0)
        return all(c)

    messages = len(
        await message.channel.purge(
            limit=args.count, check=check, oldest_first=args.oldest_first
        )
    )

    if not args.delete_command:
        try:
            await utils.reply(
                message,
                f"purged **{messages}/{args.count} {'message' if args.count == 1 else 'messages'}**",
            )
        except Exception:
            pass
