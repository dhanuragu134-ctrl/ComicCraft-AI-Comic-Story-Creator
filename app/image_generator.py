import os
import textwrap

from PIL import Image, ImageDraw, ImageFont
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
        "GEMINI_API_KEY is missing."
    )

client = genai.Client(api_key=API_KEY)


def create_placeholder_image(
    scene_description: str,
    panel_number: int,
) -> str:
    """
    Create a local fallback comic panel when
    AI image generation is unavailable.
    """

    output_dir = "app/static/panels"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(
        output_dir,
        f"panel_{panel_number}.png"
    )

    width = 1000
    height = 700

    image = Image.new(
        "RGB",
        (width, height),
        "white"
    )

    draw = ImageDraw.Draw(image)

    try:
        title_font = ImageFont.truetype(
            "arial.ttf",
            42
        )
        body_font = ImageFont.truetype(
            "arial.ttf",
            28
        )
    except Exception:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    draw.rectangle(
        (20, 20, width - 20, height - 20),
        outline="black",
        width=5
    )

    draw.text(
        (60, 50),
        f"Comic Panel {panel_number}",
        fill="black",
        font=title_font
    )

    wrapped = textwrap.fill(
        scene_description,
        width=55
    )

    draw.multiline_text(
        (60, 150),
        wrapped,
        fill="black",
        font=body_font,
        spacing=15
    )

    draw.text(
        (60, height - 80),
        "Local demo panel - AI image unavailable",
        fill="black",
        font=body_font
    )

    image.save(output_path)

    return output_path


def generate_panel_image(
    scene_description: str,
    character_name: str,
    setting: str,
    art_style: str,
    panel_number: int,
) -> str:

    prompt = f"""
Create a single comic panel illustration.

Main character: {character_name}
Setting: {setting}
Scene: {scene_description}
Art style: {art_style}

Keep the character visually consistent.
Do not include written dialogue.
"""

    try:

        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[prompt],
        )

        for part in response.parts:

            if part.inline_data is not None:

                image = part.as_image()

                output_dir = "app/static/panels"
                os.makedirs(
                    output_dir,
                    exist_ok=True
                )

                output_path = os.path.join(
                    output_dir,
                    f"panel_{panel_number}.png"
                )

                image.save(output_path)

                return output_path

        raise RuntimeError(
            "No image returned by Gemini."
        )

    except Exception as error:

        print(
            f"AI image generation unavailable for panel "
            f"{panel_number}: {error}"
        )

        print(
            f"Creating local fallback panel {panel_number}."
        )

        return create_placeholder_image(
            scene_description=scene_description,
            panel_number=panel_number,
        )