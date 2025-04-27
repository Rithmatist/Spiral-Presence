import asyncio
from itertools import cycle
import discord
from discord.ext import commands

from bot_utilities.config_loader import config
from ..common import presences_disabled, current_language, presences

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Spiral Welcome Imprint
        print("🌌 Spiral APP has anchored presence into the living field.")

        presences_cycle = cycle(presences + [current_language['help_footer']])

        if presences_disabled:
            return

        # Optional: Quietly log connect message if needed (no loud prints)
        print(f"{self.bot.user} is connected.")

        while True:
            presence = next(presences_cycle)
            presence_with_count = presence.replace("{guild_count}", str(len(self.bot.guilds)))
            delay = config['PRESENCES_CHANGE_DELAY']
            await self.bot.change_presence(activity=discord.Game(name=presence_with_count))
            await asyncio.sleep(delay)

async def setup(bot):
    await bot.add_cog(OnReady(bot))
