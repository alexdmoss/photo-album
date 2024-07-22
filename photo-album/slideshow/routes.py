import tempfile
import zipfile
import os

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import FileResponse
from jinja2_fragments.fastapi import Jinja2Blocks
from starlette.background import BackgroundTask
from starlette.responses import RedirectResponse

from slideshow.logger import log
from slideshow.config import Settings
from slideshow.images import load_images
from slideshow.auth import oauth, get_user

settings = Settings()
templates = Jinja2Blocks(directory=settings.TEMPLATE_DIR)

router = APIRouter()


templates.env.filters['strftime'] = lambda value, format='%d/%m/%Y': datetime.strptime(value, '%Y-%m-%d').strftime(format)



@router.get("/")
async def index(request: Request):
    email = None
    user = request.session.get('user')
    if user is not None:
        email = user['email']

    return templates.TemplateResponse(
        "main.html",
        {
            "site_name": "Alex's Photo Albums",
            "page_title": "Home",
            "page_description": "Alex's Photo Slideshows",
            "request": request,
            "email": email,
        }
    )


@router.get("/health")
async def healthz(request: Request):
    return "OK"


@router.get("/daisy")
async def daisy(request: Request, user: Optional[dict] = Depends(get_user)):
    if user is None:
        # User is not authenticated, redirect to login
        return templates.TemplateResponse(
            "login.html",
            {
                "site_name": "Login",
                "request": request,
            }
        )
    else:
        return templates.TemplateResponse(
            "daisy.html",
            {
                "site_name": "Daisy's 40th Birthday",
                "page_title": "Daisy",
                "page_description": "Photo Slideshow for Daisy's 40th Birthday",
                "show_controls": True,
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
        temp_zip.close()  # close the file so zipfile can open it

        # Create a zip file and add all files from PHOTOS_DIR
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(settings.PHOTOS_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, settings.PHOTOS_DIR))

        return FileResponse(
            path=zip_path,
            filename="photos.zip",
            media_type='application/zip',
            background=BackgroundTask(os.unlink, zip_path))
    except Exception as e:
        # If something goes wrong, ensure the temporary file is deleted
        os.unlink(zip_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    log.info(f"Login request for [{redirect_uri}]")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.route('/auth/google')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    request.session['user'] = token['userinfo']     # save the user
    return RedirectResponse(url='/')


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
