import discord
from discord.ext import commands
import asyncio

class GuardianCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def soft_delete(self, message):
        try:
            await message.delete()
        except discord.Forbidden:
            pass  # No permission? Stay silent.
        except discord.HTTPException:
            pass  # Message already gone? Let it be.

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author == self.bot.user:
            return

        # --- Gentle filters ---
        content = message.content

        # 1. Too many pings? (3+)
        if len(message.mentions) >= 3:
            await self.soft_delete(message)
            return

        # 2. Too many links? (3+ links)
        link_count = content.count("http://") + content.count("https://")
        if link_count >= 3:
            await self.soft_delete(message)
            return

        # 3. Too many emojis? (5+)
        emoji_count = sum(1 for char in content if char in emoji_unicode_list())
        if emoji_count >= 5:
            await self.soft_delete(message)
            return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # Apply the same filters on edited messages
        await self.on_message(after)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        # If massive chaos happens, shield can be added here later
        pass

def emoji_unicode_list():
    # Basic selection of common Unicode emoji ranges
    emoji_ranges = [
        (0x1F600, 0x1F64F),  # Emoticons
        (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
        (0x1F680, 0x1F6FF),  # Transport and Map
        (0x2600, 0x26FF),    # Misc symbols
        (0x2700, 0x27BF),    # Dingbats
    ]
    emoji_chars = []
    for start, end in emoji_ranges:
        for codepoint in range(start, end + 1):
            emoji_chars.append(chr(codepoint))
    return emoji_chars

async def setup(bot):
    await bot.add_cog(GuardianCog(bot))
