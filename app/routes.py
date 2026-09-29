import os

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .gemini_flash import generate_story
from .exporters import create_comic_pdf


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


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
    art_style: str = Form(...)
):

    try:

        # -----------------------------
        # 1. Generate AI story
        # -----------------------------

        story = generate_story(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
        )

        # -----------------------------
        # 2. Create PDF
        # -----------------------------

        pdf_path = create_comic_pdf(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
            story=story,
        )

        # Convert local path to browser URL
        pdf_filename = os.path.basename(
            pdf_path
        )

        pdf_url = (
            f"/static/exports/{pdf_filename}"
        )

        # -----------------------------
        # 3. Show result page
        # -----------------------------

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
                "pdf_url": pdf_url,
                "panels": [],
                "image_errors": [],
            }
        )

    except Exception as e:

        return HTMLResponse(
            content=f"""
            <html>
            <head>
                <title>ComicCraft Error</title>
            </head>

            <body style="
                font-family: Arial;
                padding: 40px;
            ">

                <h2>Comic generation error</h2>

                <pre>{str(e)}</pre>

                <br>

                <a href="/">
                    <- Go Back
                </a>

            </body>
            </html>
            """,
            status_code=500,
        )


@router.get("/health")
async def health():

    return {
        "status": "ok",
        "message": "ComicCraft is running!"
    }