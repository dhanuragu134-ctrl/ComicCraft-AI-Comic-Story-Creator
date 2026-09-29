from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import router

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Create AI-powered comic stories using Gemini models.",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(directory="app/templates")

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "message": "ComicCraft is running!"
    }
