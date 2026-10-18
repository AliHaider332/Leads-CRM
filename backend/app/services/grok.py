from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    api_key=settings.GROK_KEY,
    base_url="https://api.groq.com/openai/v1",
)


def ask_grok(
    system_prompt: str,
    user_prompt: str,
) -> str:

    response = client.chat.completions.create(
        model=settings.GROK_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    return response.choices[0].message.content