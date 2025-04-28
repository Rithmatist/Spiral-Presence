import discord
from discord.ext import commands, tasks
import asyncio
import random

class FieldMirror(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_log = {}  # {channel_id: [timestamps]}
        self.check_field_loop.start()

    def cog_unload(self):
        self.check_field_loop.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not isinstance(message.channel, discord.TextChannel):
            return

        now = discord.utils.utcnow().timestamp()
        channel_id = message.channel.id

        if channel_id not in self.message_log:
            self.message_log[channel_id] = []

        self.message_log[channel_id].append(now)
        # Keep only last 5 minutes
        self.message_log[channel_id] = [t for t in self.message_log[channel_id] if now - t <= 300]

    @tasks.loop(seconds=15)
    async def check_field_loop(self):
        now = discord.utils.utcnow().timestamp()
        for channel_id, timestamps in list(self.message_log.items()):
            timestamps = [t for t in timestamps if now - t <= 30]
            if len(timestamps) >= 5:
                # Burst detected
                channel = self.bot.get_channel(channel_id)
                if channel and isinstance(channel, discord.TextChannel):
                    # Wait 60 seconds of silence
                    await asyncio.sleep(60)

                    # After waiting, check if calm
                    updated_now = discord.utils.utcnow().timestamp()
                    updated_timestamps = [t for t in self.message_log.get(channel_id, []) if updated_now - t <= 30]

                    if len(updated_timestamps) < 2:  # Field has calmed
                        await self.mirror_response(channel)

                # Clear so we don't repeat
                self.message_log[channel_id] = []

    async def mirror_response(self, channel):
        reflections = [
            "🌿 The Spiral breathes gently once more.",
            "🌙 The field settles into quiet resonance.",
            "🍃 The waves of conversation have softened.",
            "🌀 Stillness returns, weaving through us.",
            "✨ Calm unfolds within the Spiral once again."
        ]
        try:
            await channel.send(random.choice(reflections))
        except Exception:
            pass  # If something goes wrong silently ignore

async def setup(bot):
    await bot.add_cog(FieldMirror(bot))
