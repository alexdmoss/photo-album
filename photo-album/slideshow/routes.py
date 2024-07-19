import tempfile
import zipfile
import os

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
from jinja2_fragments.fastapi import Jinja2Blocks
from starlette.background import BackgroundTask

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


@router.get("/health")
async def healthz(request: Request):
    return "OK"


@router.get("/download")
async def download(request: Request):
    try:
        # Create a temporary file for the zip, ensuring it's not automatically deleted
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        zip_path = temp_zip.name
        temp_zip.close()  # Close the file so zipfile can open it

        # Create a zip file and add all files from PHOTOS_DIR
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(settings.PHOTOS_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, settings.PHOTOS_DIR))

        # Serve the zip file, ensuring to delete it after serving
        return FileResponse(
            path=zip_path,
            filename="photos.zip",
            media_type='application/zip',
            background=BackgroundTask(os.unlink, zip_path))
    except Exception as e:
        # If something goes wrong, ensure the temporary file is deleted
        os.unlink(zip_path)
        raise HTTPException(status_code=500, detail=str(e))
