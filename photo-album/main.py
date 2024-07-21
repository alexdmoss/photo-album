import subprocess
import logging
import logging.config

from os import getenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from slideshow.config import settings
from slideshow.routes import router
from slideshow.secret import read_auth_api_secret, get_value_from_secret

logging.config.fileConfig(f"{settings.APP_DIR}/../logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

SECRET_KEY = get_value_from_secret(read_auth_api_secret(), "secret-key")


# context manager runs on app startup to init tailwind
@asynccontextmanager
async def lifespan(app: FastAPI):

    # makes skippable to speed up container start. Assumes main.css is in git
    if getenv("SKIP_TAILWIND_GENERATION", "false") != "true":
        try:
            logging.info("Generating Tailwind classes")
            subprocess.run([
                "tailwindcss",
                "-i",
                str(settings.STATIC_DIR / "src" / "tw.css"),
                "-o",
                str(settings.STATIC_DIR / "css" / "main.css"),
            ])
        except Exception as e:
            logging.error(f"Error running tailwindcss: {e}")

    yield


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, **settings.fastapi_kwargs)
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
    app.mount("/photos", StaticFiles(directory=settings.PHOTOS_DIR), name="photos")
    app.include_router(router)
    return app


app = get_app()

logging.info('Uvicorn is starting up ...')


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
