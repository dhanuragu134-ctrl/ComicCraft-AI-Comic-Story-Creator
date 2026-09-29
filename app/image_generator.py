import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image"
)

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from the .env file."
    )

client = genai.Client(api_key=API_KEY)


def generate_panel_image(
    scene_description: str,
    character_name: str,
    setting: str,
    art_style: str,
    panel_number: int,
) -> str:

    prompt = f"""
Create a single comic panel illustration.

Panel number: {panel_number}

Main character:
{character_name}

Setting:
{setting}

Scene:
{scene_description}

Art style:
{art_style}

Requirements:
- Keep the main character visually consistent.
- Create a clear comic-panel composition.
- Make it colorful and visually appealing.
- Do not add written dialogue.
- Do not add speech bubbles.
- Suitable for a general audience.
"""

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=[prompt],
    )

    output_dir = "app/static/panels"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(
        output_dir,
        f"panel_{panel_number}.png"
    )

    for part in response.parts:

        if part.inline_data is not None:

            image = part.as_image()

            image.save(output_path)

            return output_path

    raise RuntimeError(
        "Gemini did not return an image."
    )