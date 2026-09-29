import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = os.getenv(
    "GEMINI_FLASH_MODEL",
    "gemini-3.5-flash-lite"
)


if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Please add it to the .env file."
    )


client = genai.Client(
    api_key=API_KEY
)


def generate_outline(user_prompt: str) -> list:
    """
    Generate a structured 5-panel comic outline.

    Each panel contains:
    - panel
    - title
    - scene_description
    - image_prompt
    """

    prompt = f"""
Create a structured 5-panel comic outline from this story idea:

{user_prompt}

Return ONLY valid JSON.

The JSON must be a list containing exactly 5 objects.

Each object must contain exactly these fields:

panel
title
scene_description
image_prompt

Example structure:

[
  {{
    "panel": 1,
    "title": "The Beginning",
    "scene_description": "A short description of the scene.",
    "image_prompt": "A detailed visual prompt for the comic illustration."
  }}
]

Make the five panels form one complete story.
Keep the character, setting, and visual style consistent.
Make image_prompt detailed enough for an image-generation model.
Do not include markdown or ```json code fences.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    output_text = (response.text or "").strip()

    if not output_text:
        raise RuntimeError(
            "Gemini Flash returned an empty outline."
        )

    # Remove markdown code fences if Gemini returns them.
    if output_text.startswith("```json"):
        output_text = (
            output_text
            .replace("```json", "", 1)
            .replace("```", "")
            .strip()
        )

    elif output_text.startswith("```"):
        output_text = (
            output_text
            .replace("```", "", 2)
            .strip()
        )

    try:
        outline = json.loads(output_text)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Gemini Flash returned invalid JSON: {error}"
        )

    if not isinstance(outline, list):
        raise RuntimeError(
            "Gemini Flash outline must be a list."
        )

    if len(outline) != 5:
        raise RuntimeError(
            f"Expected 5 panels, but received {len(outline)}."
        )

    required_fields = {
        "panel",
        "title",
        "scene_description",
        "image_prompt",
    }

    for index, panel in enumerate(outline, start=1):

        if not isinstance(panel, dict):
            raise RuntimeError(
                f"Panel {index} is not a valid object."
            )

        missing_fields = required_fields - set(panel.keys())

        if missing_fields:
            raise RuntimeError(
                f"Panel {index} is missing: "
                f"{', '.join(sorted(missing_fields))}"
            )

    return outline