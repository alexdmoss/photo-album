import subprocess
import logging
import logging.config

from os import getenv
from os.path import join
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from slideshow.config import settings
from slideshow.routes import router
from slideshow.images import resize_images, list_images_in_dir
from slideshow.clients.storage import create_storage_client

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
        print(f"Error running tailwindcss: {e}")

    if getenv("RESIZE", "false").lower() == "true":
        logging.info("Resizing images as requested via environment variable")
        await resize_images()

    processed_images = list_images_in_dir(settings.TMP_DIR, ".jpg")
    if len(processed_images) == 0:
        # nothing saved locally - grab the processed images from GCS bucket instead
        print(f"-> [INFO] Downloading images from GCS [{settings.GCS_BUCKET_NAME}/{settings.GCS_BUCKET_PATH}]")
        client = create_storage_client()
        bucket = client.get_bucket(settings.GCS_BUCKET_NAME)

        blobs = bucket.list_blobs(prefix=settings.GCS_BUCKET_PATH)
        for blob in blobs:
            if blob.name.endswith('.jpg'):
                destination_file_name = join(settings.TMP_DIR, blob.name.split('/')[-1])
                blob.download_to_filename(destination_file_name)
                print(f"Downloaded {blob.name} to {destination_file_name}")

    yield


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, **settings.fastapi_kwargs)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
    app.mount("/photos", StaticFiles(directory=settings.PHOTOS_DIR), name="photos")
    app.mount("/tmp", StaticFiles(directory=settings.TMP_DIR), name="tmp")
    app.include_router(router)
    return app


app = get_app()

logging.info('Uvicorn is starting up ...')


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
