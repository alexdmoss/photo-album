from pathlib import Path
from typing import Any

from fastapi.responses import HTMLResponse
from pydantic_settings import BaseSettings

APP_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):

    APP_DIR: Path = APP_DIR
    STATIC_DIR: Path = APP_DIR / "static"
    TEMPLATE_DIR: Path = APP_DIR / "templates"
    PHOTOS_DIR: Path = APP_DIR / "../../photos"             # @TODO: make configurable
    TMP_DIR: Path = APP_DIR / "../../tmp"                   # @TODO: make configurable
    GCS_BUCKET_NAME: str = "alexos-photo-albums"            # @TODO: make configurable
    GCS_BUCKET_PATH: str = "daisy-40/processed"             # @TODO: make configurable

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
