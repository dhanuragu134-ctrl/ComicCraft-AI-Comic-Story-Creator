import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

PRO_MODEL = os.getenv(
    "GEMINI_PRO_MODEL",
    "gemini-3.1-pro-preview"
)

FALLBACK_MODEL = os.getenv(
    "GEMINI_STORY_FALLBACK_MODEL",
    "gemini-3.5-flash-lite"
)


if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from the .env file."
    )


client = genai.Client(
    api_key=API_KEY
)


def build_prompt(outline: list) -> str:

    formatted_outline = []

    for panel in outline:

        formatted_outline.append(
            f"""
Panel {panel.get("panel", "")}
Title: {panel.get("title", "")}
Scene Description: {panel.get("scene_description", "")}
Image Prompt: {panel.get("image_prompt", "")}
"""
        )

    outline_text = "\n".join(
        formatted_outline
    )

    return f"""
Write a complete five-panel comic story from this outline.

{outline_text}

For every panel provide:

Panel 1
Title:
Narration:
Dialogue:

Panel 2
Title:
Narration:
Dialogue:

Panel 3
Title:
Narration:
Dialogue:

Panel 4
Title:
Narration:
Dialogue:

Panel 5
Title:
Narration:
Dialogue:

Requirements:
- Keep the same main character throughout.
- Follow the outline closely.
- Include short narration and character dialogue.
- Keep the story suitable for a general audience.
- Do not add extra panels.
"""


def generate_story(outline: list) -> str:

    if not outline:
        raise RuntimeError(
            "Comic outline is empty."
        )

    prompt = build_prompt(outline)

    # Try the required Pro model first.
    try:

        print(
            f"Trying story model: {PRO_MODEL}"
        )

        response = client.models.generate_content(
            model=PRO_MODEL,
            contents=prompt,
        )

        story = (response.text or "").strip()

        if story:
            print(
                f"Story generated successfully using {PRO_MODEL}"
            )
            return story

    except Exception as pro_error:

        print(
            f"Pro model unavailable: {pro_error}"
        )

        # Fall back to Flash when Pro is unavailable/quota-exhausted.
        error_text = str(pro_error)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "503" in error_text
            or "UNAVAILABLE" in error_text
        ):
            print(
                f"Using fallback story model: {FALLBACK_MODEL}"
            )

        else:
            raise

    # Fallback model
    try:

        response = client.models.generate_content(
            model=FALLBACK_MODEL,
            contents=prompt,
        )

        story = (response.text or "").strip()

        if story:
            print(
                f"Story generated successfully using {FALLBACK_MODEL}"
            )
            return story

        raise RuntimeError(
            "Fallback model returned an empty story."
        )

    except Exception as fallback_error:

        raise RuntimeError(
            "Both the Pro model and fallback story model failed. "
            f"Last error: {fallback_error}"
        )