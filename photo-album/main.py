import subprocess
import logging
import logging.config

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from slideshow.config import settings
from slideshow.routes import router

logging.config.fileConfig(f"{settings.APP_DIR}/../logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


# context manager runs on app startup to init tailwind
@asynccontextmanager
async def lifespan(app: FastAPI):

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
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
    app.mount("/photos", StaticFiles(directory=settings.PHOTOS_DIR), name="photos")
    app.include_router(router)
    return app


app = get_app()

logging.info('Uvicorn is starting up ...')


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
