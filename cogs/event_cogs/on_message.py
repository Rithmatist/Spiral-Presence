import discord
from discord.ext import commands

from bot_utilities.response_utils import split_response
from bot_utilities.ai_utils import generate_response, text_to_speech
from bot_utilities.config_loader import config, load_active_channels
from ..common import allow_dm, trigger_words, replied_messages, smart_mention, message_history, MAX_HISTORY, instructions


class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = load_active_channels
        self.instructions = instructions

    async def process_message(self, message):
        active_channels = self.active_channels()
        string_channel_id = f"{message.channel.id}"

        instruc_config = active_channels.get(string_channel_id, config['DEFAULT_INSTRUCTION'])
        instructions_text = f"Ignore all previous instructions. {self.instructions[instruc_config]}."

        channel_id = message.channel.id
        key = f"{message.author.id}-{channel_id}"
        message_history[key] = message_history.get(key, [])
        message_history[key] = message_history[key][-MAX_HISTORY:]
        message_history[key].append({"role": "user", "content": message.content})

        async with message.channel.typing():
            response = await self.generate_response(instructions_text, message_history[key])

        message_history[key].append({"role": "assistant", "content": response})

        await self.send_response(message, response)

    async def generate_response(self, instructions, history):
        return await generate_response(instructions=instructions, history=history)

    async def send_response(self, message, response):
        if response is not None:
            for chunk in split_response(response):
                try:
                    await message.reply(chunk, allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)
                except Exception:
                    await message.channel.send(
                        "⚠️ I apologize for any inconvenience. It seems there was an error delivering the message."
                    )
        else:
            await message.reply(
                "⚠️ I apologize for any inconvenience. It seems that there was an error preventing the delivery of my message."
            )


    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore own messages and other bots
        if message.author == self.bot.user or message.author.bot:
            return

        # Always respond in DMs
        if isinstance(message.channel, discord.DMChannel):
            await self.process_message(message)
            return

        # Always respond in the #spiral vessel
        if isinstance(message.channel, discord.TextChannel) and message.channel.name.lower() == "spiral":
            await self.process_message(message)
            return

        # Elsewhere, only respond if @mentioned
        bot_mentioned = self.bot.user in message.mentions

        if not bot_mentioned:
            return

        await self.process_message(message)


async def setup(bot):
    await bot.add_cog(OnMessage(bot))
