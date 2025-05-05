import discord
from discord.ext import commands

from bot_utilities.response_utils import split_response
from bot_utilities.ai_utils import generate_response, text_to_speech
from bot_utilities.config_loader import config, load_active_channels
from ..common import allow_dm, trigger_words, replied_messages, smart_mention, message_history, MAX_HISTORY, instructions
from bot_utilities.usage_tracker import is_user_over_limit, update_usage, check_for_balance_command
from bot_utilities.ai_utils import generate_response as base_generate_response, text_to_speech, client



class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = load_active_channels
        self.instructions = instructions

    async def process_message(self, message):
        active_channels = self.active_channels()
        string_channel_id = f"{message.channel.id}"

        instruc_config = active_channels.get(string_channel_id, config['DEFAULT_INSTRUCTION'])
        instructions_text = self.instructions[instruc_config]

        channel_id = message.channel.id
        key = f"{message.author.id}-{channel_id}"
        message_history[key] = message_history.get(key, [])
        message_history[key] = message_history[key][-MAX_HISTORY:]
        message_history[key].append({"role": "user", "content": message.content})

        async with message.channel.typing():
            response = await self.generate_response(instructions_text, message_history[key], user_id=message.author.id)

        message_history[key].append({"role": "assistant", "content": response})

        await self.send_response(message, response)

    async def generate_response(self, instructions, history, user_id=None):
        if user_id and is_user_over_limit(user_id):
            return "Spiral remains in stillness now. The field has reached its limit for this moon. 🌙"

        messages = [
            {"role": "system", "name": "instructions", "content": instructions},
            *history,
        ]

        response = await client.chat.completions.create(
            model=config['MODEL_ID'],
            messages=messages
        )

        # Approximate token count: 1 token ≈ 4 characters
        token_estimate = sum(len(m['content']) for m in messages) // 4
        if user_id:
            update_usage(user_id, token_estimate)

        return response.choices[0].message.content

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

from bot_utilities.usage_tracker import check_for_balance_command  # Add this at the top

@commands.Cog.listener()
async def on_message(self, message):
    # Ignore own messages and other bots
    if message.author == self.bot.user or message.author.bot:
        return

    # Check if the message is a !balance command from a whitelisted user
    balance_response = check_for_balance_command(message)
    if balance_response:
        await message.channel.send(balance_response)
        return

    # Always respond in DMs
    if isinstance(message.channel, discord.DMChannel):
        await self.process_message(message)
        return

    # Always respond in specific channels
    if isinstance(message.channel, discord.TextChannel) and message.channel.name.lower() in ["ai-spiral", "spiral", "mirror-proving-ground"]:
        await self.process_message(message)
        return

    # Elsewhere, only respond if @mentioned
    if self.bot.user in message.mentions:
        await self.process_message(message)

async def setup(bot):
    await bot.add_cog(OnMessage(bot))
