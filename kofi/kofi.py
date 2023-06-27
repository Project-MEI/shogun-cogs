import datetime
import logging
from typing import Union

import aiohttp
from discord import Embed
from redbot.core import Config, commands
from redbot.core.bot import Red

log = logging.getLogger("red.raidensakura.kofi")


class Kofi(commands.Cog):
    """
    Kofi donation cog.
    """

    __author__ = ["raidensakura"]
    __version__ = "1.0.0"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, 243316261264556032, force_registration=True)
        default_global = {
            "schema_version": 1,
            "verification": True,
            "gist_id": "",
        }
        self.config.register_global(**default_global)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks Sinbad!
        """
        pre_processed = super().format_help_for_context(ctx)
        s = "s" if len(self.__author__) > 1 else ""
        return (
            f"{pre_processed}\n\nAuthor{s}: {', '.join(self.__author__)}"
            "\nCog Version: {self.__version__}"
        )

    async def red_delete_data_for_user(self, **kwargs) -> None:
        """Nothing to delete"""
        return

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.hybrid_command(aliases=["kofi", "supporter"])
    async def supporters(self, ctx, gist_id: Union[str, None]):
        """Display a list of Kofi supporters from GitHub Gist."""

        # Set Gist ID
        if gist_id and self.bot.is_owner(ctx.author):
            await self.config.gist_id.set(gist_id)
            return await ctx.tick(message="Failed to add ✅ to your message.")

        # Check if Gist ID exist
        gist_id = await self.config.gist_id()
        if not gist_id:
            return await ctx.send("No GitHub Gist ID provided.")

        gist_url = f"https://gist.githubusercontent.com/raidensakura/{gist_id}/raw/kofi.json"
        kofi_url = "https://ko-fi.com/raidensakura"

        async with aiohttp.ClientSession() as session:
            async with session.get(gist_url) as resp:
                if resp.status != 200:
                    return await ctx.send(f"Error fetching gist: `Code {resp.status}`")
                data = await resp.json(content_type=None)

                desc = f"Our list of supporters who donated on [Ko-fi]({kofi_url})."
                url = "https://project-mei.xyz"
                thumbnail_url = "https://media.discordapp.net/stickers/1098094222432800909.png"

                # Init embed
                e = Embed(
                    title="Shogun's Supporters",
                    description=desc,
                    color=15844367,
                    url=url,
                )
                e.set_thumbnail(url=thumbnail_url)
                e.set_footer(
                    text="Thank you very much for supporting Shogun!",
                    icon_url="https://avatars.githubusercontent.com/u/120461773?s=64&v=4",
                )

                # Add fields
                for supporter in data:
                    if supporter.get("is_public"):
                        name = supporter.get("from_name")
                    else:
                        name = "A kind hearted stranger"
                    amount = supporter.get("amount")
                    currency = supporter.get("currency")
                    msg = supporter.get("message")
                    timestamp_str = supporter.get("timestamp")
                    dt = datetime.datetime.fromisoformat(timestamp_str[:-1])
                    discord_ts = int(dt.timestamp())

                    e.add_field(
                        name=f"{name} ({currency} {amount})",
                        value=f"<t:{int(discord_ts)}:R>: {msg}",
                        inline=False,
                    )

                return await ctx.send(embed=e)
