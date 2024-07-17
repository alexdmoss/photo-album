from typing import Annotated

from fastapi import APIRouter, Form, Request
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import BaseModel

from slideshow.config import Settings
from slideshow.images import load_images

settings = Settings()
templates = Jinja2Blocks(directory=settings.TEMPLATE_DIR)

router = APIRouter()


@router.get("/")
async def index(request: Request):
    images = await load_images()
    return templates.TemplateResponse(
            "main.html",
            {
                "site_name": "Daisy's 40th Birthday",
                "page_title": "Home",
                "page_description": "Photo Slideshow for Daisy's 40th Birthday",
                "images": images,
                "request": request,
            }
        )
