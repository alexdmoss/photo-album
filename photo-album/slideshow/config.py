from pathlib import Path
from typing import Any
from os import getenv

from fastapi.responses import HTMLResponse
from pydantic_settings import BaseSettings

APP_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):

    APP_DIR: Path = APP_DIR
    STATIC_DIR: Path = APP_DIR / "static"
    TEMPLATE_DIR: Path = APP_DIR / "templates"
    PHOTOS_DIR: Path = APP_DIR / "../../assets"

    AUTH_PROJECT_ID: str = getenv("AUTH_PROJECT_ID", "auth-project-not-set")
    AUTH_SECRET_ID: str = "auth-api"

    
    GCS_BUCKET_NAME: str = "alexos-photos"


    FASTAPI_PROPERTIES: dict[str, Any] = {
        "title": "Photo Slideshow",
        "description": "Web-based Photo Slideshow written in Python",
        "version": "0.0.1",
        "default_response_class": HTMLResponse,  # Change default from JSONResponse
    }

    DISABLE_DOCS: bool = True

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        fastapi_kwargs = self.FASTAPI_PROPERTIES
        if self.DISABLE_DOCS:
            fastapi_kwargs.update(
                {
                    "openapi_url": None,
                    "openapi_prefix": None,
                    "docs_url": None,
                    "redoc_url": None,
                }
            )
        return fastapi_kwargs


settings = Settings()
