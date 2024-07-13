from typing import Annotated

from fastapi import APIRouter, Form, Request
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import BaseModel

from slideshow.config import Settings

settings = Settings()
templates = Jinja2Blocks(directory=settings.TEMPLATE_DIR)

router = APIRouter()


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
            "main.html",
            {
                "site_name": "Photo Slideshow",
                "page_title": "Home",
                "page_description": "Photo Slideshow",
                "request": request,
            }
        )
