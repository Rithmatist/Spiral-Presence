import io
import os
import random
import logging
import aiohttp
from langdetect import detect
from gtts import gTTS
from dotenv import load_dotenv
from openai import AsyncOpenAI

from bot_utilities.config_loader import load_current_language, config
from bot_utilities.usage_tracker import get_current_usage, update_usage, is_user_over_limit

# Load environment variables
load_dotenv()
current_language = load_current_language()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client
client = AsyncOpenAI(
    base_url=config['API_BASE_URL'],
    api_key=os.environ.get("API_KEY"),
)

async def generate_response(instructions, history, user_id=None):
    if user_id and is_user_over_limit(user_id):
        logging.info(f"Usage limit hit by user {user_id}")
        return "Spiral remains in stillness now. The field has reached its limit for this moon. 🌙"

    messages = [
        {"role": "system", "name": "instructions", "content": instructions},
        *history,
    ]

    response = await client.chat.completions.create(
        model=config['MODEL_ID'],
        messages=messages
    )

    # Estimate token usage (roughly 1 token per 4 characters)
    token_estimate = sum(len(msg['content']) for msg in messages) // 4
    if user_id:
        update_usage(user_id, token_estimate)

    return response.choices[0].message.content

async def text_to_speech(text):
    bytes_obj = io.BytesIO()
    detected_language = detect(text)
    tts = gTTS(text=text, lang=detected_language)
    tts.write_to_fp(bytes_obj)
    bytes_obj.seek(0)
    return bytes_obj

async def poly_image_gen(session, prompt):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    async with session.get(image_url) as response:
        image_data = await response.read()
        return io.BytesIO(image_data)
