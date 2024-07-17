import subprocess

from os import getenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from slideshow.config import settings
from slideshow.routes import router
from slideshow.images import resize_images

# context manager runs on app startup to init tailwind
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        subprocess.run([
            "tailwindcss",
            "-i",
            str(settings.STATIC_DIR / "src" / "tw.css"),
            "-o",
            str(settings.STATIC_DIR / "css" / "main.css"),
        ])
    except Exception as e:
        print(f"Error running tailwindcss: {e}")

    if getenv("resize", "false").lower() == "true":
        await resize_images()

    yield


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, **settings.fastapi_kwargs)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
    app.mount("/photos", StaticFiles(directory=settings.PHOTOS_DIR), name="photos")
    app.mount("/tmp", StaticFiles(directory=settings.TMP_DIR), name="tmp")
    app.include_router(router)
    return app


app = get_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
