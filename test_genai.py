import asyncio
import os
from google import genai
from google.genai import types

async def main():
    try:
        from app.core.settings import get_settings
        settings = get_settings()
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.0-flash',  # or whatever model works
            contents='my account is locked help me',
        )
        print("GenAI result:", response.text)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
