import re
from typing import Any

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .models import PromptRequest
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_panel_image
from .layout_builder import build_comic_layout
from .exporters import create_comic_pdf


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


def split_story_by_panel(story: str) -> dict[int, str]:
    """
    Split Gemini's story into Panel 1 ... Panel 5 sections.
    """

    pattern = r"(?=Panel\s+\d+\b)"
    parts = re.split(
        pattern,
        story,
        flags=re.IGNORECASE
    )

    result = {}

    for part in parts:

        part = part.strip()

        match = re.match(
            r"Panel\s+(\d+)",
            part,
            flags=re.IGNORECASE
        )

        if match:
            number = int(match.group(1))
            result[number] = part

    return result


def build_panel_records(
    outline: list[dict[str, Any]],
    story: str
) -> list[dict[str, Any]]:

    story_panels = split_story_by_panel(story)

    panels = []

    for index, outline_panel in enumerate(
        outline,
        start=1
    ):

        panel_number = int(
            outline_panel.get(
                "panel",
                index
            )
        )

        panels.append(
            {
                "panel": panel_number,
                "title": outline_panel.get(
                    "title",
                    f"Panel {panel_number}"
                ),
                "scene_description": outline_panel.get(
                    "scene_description",
                    ""
                ),
                "image_prompt": outline_panel.get(
                    "image_prompt",
                    ""
                ),
                "text": story_panels.get(
                    panel_number,
                    ""
                ),
                "image_path": "",
            }
        )

    return panels


def generate_panel_images(
    panels: list[dict[str, Any]],
    character_name: str,
    setting: str,
    art_style: str,
) -> tuple[list[dict[str, Any]], list[str]]:

    updated_panels = []
    image_errors = []

    for panel in panels:

        try:

            image_path = generate_panel_image(
                scene_description=panel["image_prompt"],
                character_name=character_name,
                setting=setting,
                art_style=art_style,
                panel_number=panel["panel"],
            )

            panel["image_path"] = image_path

        except Exception as error:

            image_errors.append(
                f"Panel {panel['panel']}: {error}"
            )

        updated_panels.append(panel)

    return updated_panels, image_errors


@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate_comic(
    request: Request,

    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):

    try:

        # ----------------------------------
        # 1. Gemini Flash - comic outline
        # ----------------------------------

        outline = generate_outline(
            story_prompt
        )

        # ----------------------------------
        # 2. Gemini Pro - story
        # ----------------------------------

        story = generate_story(
            outline
        )

        # ----------------------------------
        # 3. Build panel records
        # ----------------------------------

        panels = build_panel_records(
            outline=outline,
            story=story
        )

        # ----------------------------------
        # 4. Try image generation
        # ----------------------------------

        panels, image_errors = generate_panel_images(
            panels=panels,
            character_name=character_name,
            setting=setting,
            art_style=art_style,
        )

        # ----------------------------------
        # 5. Build comic layout
        # ----------------------------------

        layout = build_comic_layout(
            panels=panels,
            story=story
        )

        # ----------------------------------
        # 6. Create PDF
        # ----------------------------------

        pdf_path = create_comic_pdf(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
            story=story,
        )

        pdf_filename = pdf_path.replace(
            "\\",
            "/"
        ).split("/")[-1]

        pdf_url = (
            f"/static/exports/{pdf_filename}"
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "story_prompt": story_prompt,
                "character_name": character_name,
                "setting": setting,
                "tone": tone,
                "art_style": art_style,
                "story": story,
                "outline": outline,
                "panels": panels,
                "layout": layout,
                "image_errors": image_errors,
                "pdf_url": pdf_url,
            }
        )

    except Exception as error:

        return HTMLResponse(
            content=f"""
            <html>
            <body style="
                font-family: Arial;
                padding: 40px;
            ">

                <h2>Comic generation error</h2>

                <pre>{error}</pre>

                <a href="/">
                    &lt;- Go Back
                </a>

            </body>
            </html>
            """,
            status_code=500
        )


@router.post(
    "/generate-comic/json"
)
async def generate_comic_json(
    data: PromptRequest
):

    try:

        outline = generate_outline(
            data.story_prompt
        )

        story = generate_story(
            outline
        )

        panels = build_panel_records(
            outline=outline,
            story=story
        )

        layout = build_comic_layout(
            panels=panels,
            story=story
        )

        pdf_path = create_comic_pdf(
            story_prompt=data.story_prompt,
            character_name=data.character_name,
            setting=data.setting,
            tone=data.tone,
            art_style=data.art_style,
            story=story,
        )

        return {
            "success": True,
            "outline": outline,
            "story": story,
            "layout": layout,
            "pdf_path": pdf_path,
        }

    except Exception as error:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(error)
            }
        )


@router.post(
    "/test-image"
)
async def test_image(
    prompt: str = Form(...)
):

    try:

        image_path = generate_panel_image(
            scene_description=prompt,
            character_name="Test Character",
            setting="Fantasy world",
            art_style="Comic book",
            panel_number=99,
        )

        return {
            "success": True,
            "image_path": image_path
        }

    except Exception as error:

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(error)
            }
        )


@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={}
    )


@router.get("/health")
async def health():

    return {
        "status": "ok",
        "message": "ComicCraft is running!"
    }