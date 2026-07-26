import requests
from config import GEMINI_API_KEY, SYSTEM_PROMPT

MODEL = "gemini-3.5-flash"


def ask_gemini(user_message, history=None, user_memory=None):
    if history is None:
        history = []

    if user_memory is None:
        user_memory = {}

    conversation = "\n".join(
        [str(item) for item in history[-20:]]
    )

    memory_text = ""

    if user_memory.get("name"):
        memory_text += f"User name: {user_memory['name']}\n"

    if user_memory.get("facts"):
        memory_text += f"Known facts: {user_memory['facts']}\n"

    if user_memory.get("preferences"):
        memory_text += f"Preferences: {user_memory['preferences']}\n"

    prompt = f"""
{SYSTEM_PROMPT}

User information:
{memory_text}

Previous conversation:
{conversation}

Current user message:
{user_message}

Answer naturally and remember the context.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=60
    )

    response.raise_for_status()

    result = response.json()

    return result["candidates"][0]["content"]["parts"][0]["text"]
