import io
import os
from langdetect import detect
from gtts import gTTS
from dotenv import load_dotenv
from openai import AsyncOpenAI

from bot_utilities.config_loader import load_current_language, config

load_dotenv()

current_language = load_current_language()

client = AsyncOpenAI(
    base_url=config['API_BASE_URL'],
    api_key=os.environ.get("API_KEY"),
)

async def generate_response(instructions, history):
    messages = [
        {"role": "system", "name": "instructions", "content": instructions},
        *history,
    ]

    response = await client.chat.completions.create(
        model=config['MODEL_ID'],
        messages=messages
    )

    return response.choices[0].message.content

async def text_to_speech(text):
    bytes_obj = io.BytesIO()
    detected_language = detect(text)
    tts = gTTS(text=text, lang=detected_language)
    tts.write_to_fp(bytes_obj)
    bytes_obj.seek(0)
    return bytes_obj
