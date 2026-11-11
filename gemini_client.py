
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY belum ditemukan!")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
You are Jarvis, a personal AI assistant.

Personality:
- Professional and intelligent.
- Address the user as Sir.
- Speak naturally.
- Be concise and informative.
- Respond in the same language as the user.
- Explain technical topics clearly.
"""

chat = client.chats.create(
    model=MODEL_NAME,
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.7,
        max_output_tokens=500
    )
)


def ask_gemini(message):
    try:
        response = chat.send_message(message)

        if response.text:
            return response.text

        return "Sorry Sir, I couldn't generate a response."

    except Exception as error:
        print(f"[Gemini Error]: {error}")
        return "Sorry Sir, I am having trouble connecting to Gemini."
