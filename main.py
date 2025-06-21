from os import getenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from photo_album.logger import log
from photo_album.config import settings
from photo_album.routes import router as main_router
from photo_album.photos import router as photos_router
from photo_album.videos import router as videos_router
from photo_album.likes import router as likes_router
from photo_album.secret import read_auth_api_secret, get_value_from_secret

SECRET_KEY = get_value_from_secret(read_auth_api_secret(), "secret-key")


# context manager runs on app startup to init tailwind
@asynccontextmanager
async def lifespan(app: FastAPI):

    # makes skippable to speed up container start. Assumes main.css is in git
    if getenv("SKIP_TAILWIND_GENERATION", "false") != "true":
        try:
            import asyncio
            log.info("Generating Tailwind classes")
            process = await asyncio.create_subprocess_exec(
                "tailwindcss",
                "-i",
                str(settings.STATIC_DIR / "src" / "tw.css"),
                "-o",
                str(settings.STATIC_DIR / "css" / "main.css"),
            )
            await process.communicate()
        except Exception as e:
            log.error(f"Error running tailwindcss: {e}")

    yield


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, **settings.fastapi_kwargs)
    app.add_middleware(ProxyHeadersMiddleware)
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
    Instrumentator().instrument(app).expose(app)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
    app.mount("/assets", StaticFiles(directory=settings.PHOTOS_DIR), name="assets")
    app.include_router(main_router)
    app.include_router(photos_router)
    app.include_router(videos_router)
    app.include_router(likes_router)
    return app


app = get_app()

log.info('Uvicorn is starting up ...')


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, proxy_headers=True)
