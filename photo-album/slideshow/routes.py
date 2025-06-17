import tempfile
import zipfile
import os
import re
import uuid

from datetime import datetime

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
from jinja2_fragments.fastapi import Jinja2Blocks
from starlette.background import BackgroundTask
from starlette.responses import RedirectResponse

from slideshow.logger import log
from slideshow.config import settings
from slideshow.auth import oauth, is_user_authorised
from slideshow.albums import get_albums


def format_caption(value):
    filename = value.split('/')[-1]
    # many bothans died to provide us with this regular expression
    match = re.match(r'^(?P<date>\d{4}[-.]\d{2}[-.]\d{2})[_. ](?P<rest>.*)\.(?P<ext>[^.]+)$', filename)
    if match:
        date_string = match.group('date').replace('-', '.')
        try:
            formatted_date = datetime.strptime(date_string, '%Y.%m.%d').strftime('%d/%m/%Y')
            rest_of_name = match.group('rest')
            return f"{formatted_date}: {rest_of_name}"
        except ValueError:
            return filename.rsplit('.', 1)[0]
    else:
        return filename.rsplit('.', 1)[0]  # remove extension


templates = Jinja2Blocks(directory=settings.TEMPLATE_DIR)
templates.env.filters['format_caption'] = format_caption


router = APIRouter()


@router.get("/")
async def index(request: Request):
    email = None
    albums = None
    user = request.session.get('user')
    if user is not None:
        email = user['email']
        albums = get_albums(email)

    return templates.TemplateResponse(
        "main.html",
        {
            "site_name": "Photo Albums",
            "page_title": "Home",
            "page_description": "Alex's Photo & Video Albums",
            "request": request,
            "email": email,
            "albums": albums,
        }
    )


@router.get("/health")
async def healthz(request: Request):
    return "OK"


@router.get("/download")
async def download(request: Request):
    zip_path = None
    try:
        # Create a unique temporary file path for the zip
        zip_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.zip")
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
        if zip_path and os.path.exists(zip_path):
            os.unlink(zip_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/login')
async def login(request: Request):
    redirect_uri = str(request.url_for('auth'))
    # this workaround is because x-forwarded-proto is not being respected even when the ProxyHeadersMiddleware is enabled
    host = request.headers.get("host", "")
    if not (host.startswith("localhost") or host.startswith("127.0.0.1")):
        redirect_uri = redirect_uri.replace("http://", "https://", 1)
    log.info(f"Login request for [{redirect_uri}]")
    if not hasattr(oauth, "google") or oauth.google is None:
        log.error("OAuth provider 'google' is not configured properly.")
        raise HTTPException(status_code=500, detail="OAuth provider not configured.")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.route('/auth/google')
async def auth(request: Request):

    try:
        if not hasattr(oauth, "google") or oauth.google is None:
            log.error("OAuth provider 'google' is not configured properly.")
            raise HTTPException(status_code=500, detail="OAuth provider not configured.")

        token = await oauth.google.authorize_access_token(request)

        if is_user_authorised(token['userinfo']['email']):
            request.session['user'] = token['userinfo']
            if "origin" in request.session:
                return RedirectResponse(url=request.session["origin"])
            else:
                return RedirectResponse(url='/')

    except HTTPException as e:
        log.error(f"A HTTP Exception occurred [{e.detail}]")
        return templates.TemplateResponse(
            status_code=e.status_code,
            name="error.html",
            context={
                "site_name": "Photo Albums",
                "page_title": "Error",
                "page_description": "Alex's Photo & Video Albums",
                "error_msg": e.detail,
                "request": request,
            }
        )


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
