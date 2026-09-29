import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.5-flash-lite")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Please add it to the .env file."
    )

client = genai.Client(api_key=API_KEY)


def generate_story(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
) -> str:

    prompt = f"""
Create a short five-panel comic story.

Story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}

Return exactly five panels.

Panel 1
Scene:
Narration:
Dialogue:

Panel 2
Scene:
Narration:
Dialogue:

Panel 3
Scene:
Narration:
Dialogue:

Panel 4
Scene:
Narration:
Dialogue:

Panel 5
Scene:
Narration:
Dialogue:

Make the five panels form one complete story.
Keep the story suitable for a general audience.
Keep narration and dialogue short and clear.
"""

    delays = [5, 15, 30]
    last_error = None

    for attempt in range(3):
        try:
            print(
                f"Trying Gemini model: {MODEL} "
                f"(attempt {attempt + 1}/3)"
            )

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )

            if response.text:
                print("Gemini generation successful.")
                return response.text

            raise RuntimeError("Gemini returned an empty response.")

        except Exception as e:
            last_error = e
            error_text = str(e)

            print(f"Gemini error: {error_text}")

            if "429" in error_text or "503" in error_text:
                if attempt < 2:
                    print(f"Retrying in {delays[attempt]} seconds...")
                    time.sleep(delays[attempt])
                    continue

            raise RuntimeError(
                f"Gemini generation failed: {error_text}"
            )

    raise RuntimeError(
        f"Gemini generation failed after retries: {last_error}"
    )