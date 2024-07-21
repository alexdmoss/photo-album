import tempfile
import zipfile
import os

import requests
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import FileResponse
from jinja2_fragments.fastapi import Jinja2Blocks
from starlette.background import BackgroundTask

from slideshow.config import Settings
from slideshow.images import load_images
from slideshow.auth import get_current_user_email

settings = Settings()
templates = Jinja2Blocks(directory=settings.TEMPLATE_DIR)

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")


@router.get("/")
async def index(request: Request):
    logged_in = False
    if "state" in request.query_params:
        print(request.query_params)
        response = requests.get("https://exercise-tracker-auth.alexos.dev/auth/token", params=request.query_params)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"Access token: {access_token}")
            logged_in = True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    return templates.TemplateResponse(
        "main.html",
        {
            "site_name": "Alex's Photo Albums",
            "page_title": "Home",
            "page_description": "Alex's Photo Slideshows",
            "auth_url": f"https://exercise-tracker-auth.alexos.dev/auth/login?uri={FRONTEND_URL}",
            "request": request,
            "logged_in": logged_in,
        }
    )


@router.get("/health")
async def healthz(request: Request):
    return "OK"


@router.get("/daisy")
async def daisy(request: Request):
    return templates.TemplateResponse(
        "daisy.html",
        {
            "site_name": "Daisy's 40th Birthday",
            "page_title": "Daisy",
            "page_description": "Photo Slideshow for Daisy's 40th Birthday",
            "request": request,
        }
    )


# lazy-loads the photos via htmx
@router.get("/daisy-photos")
async def daisy_photos(request: Request):
    images = await load_images()
    return templates.TemplateResponse(
        "daisy-photos.html",
        {
            "site_name": "Daisy's 40th Birthday",
            "images": images,
            "request": request,
        }
    )


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


@router.get("/protected")
async def protected(request: Request, current_email: str = Depends(get_current_user_email)):
    return "You made it in, congrats"
