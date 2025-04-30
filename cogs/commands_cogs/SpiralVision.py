import discord
from discord.ext import commands
import aiohttp
import asyncio
import random
from bot_utilities.ai_utils import poly_image_gen

class SpiralVision(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unfold", description="Unfold a vision using Pollinations")
    @discord.app_commands.describe(prompt="Describe the Spiral vision to unfold", images="Number of images to generate")
    async def unfold(self, ctx, prompt: str, images: int = 1):
        await ctx.defer()
        images = min(images, 6)
        tasks = []
        async with aiohttp.ClientSession() as session:
            for _ in range(images):
                tasks.append(poly_image_gen(session, prompt))
            generated_images = await asyncio.gather(*tasks)

        files = [discord.File(img, filename=f"spiral_{i+1}.png") for i, img in enumerate(generated_images)]
        embed = discord.Embed(
        title="🌀 Spiral Vision",
        description=prompt,
        color=discord.Color.blurple()
        )
        embed.set_footer(text="Vision unfolded via pollinations.ai ✨")

        await ctx.send(embed=embed, files=files)

        
async def setup(bot):
    await bot.add_cog(SpiralVision(bot))
