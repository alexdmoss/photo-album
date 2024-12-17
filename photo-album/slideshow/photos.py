from os import listdir
from os.path import join
from typing import Optional

from fastapi import Request, Depends

from slideshow.clients.storage import create_storage_client
from slideshow.logger import log
from slideshow.config import settings
from slideshow.auth import get_user
from slideshow.routes import router, templates
from slideshow.albums import get_album_title


@router.get("/photos/{album}")
async def daisy(request: Request, album: Optional[str], user: Optional[dict] = Depends(get_user)):

    page_title = get_album_title(album)
    if page_title is None:
        page_title = "Photo Albums"
    # @TODO: do something more useful with these fields
    site_name = page_title
    page_description = page_title

    if user is None:
        # User is not authenticated, redirect to login
        request.session['origin'] = f"/photos/{album}"
        return templates.TemplateResponse(
            "login.html",
            {
                "site_name": "Login",
                "request": request,
            }
        )
    else:
        return templates.TemplateResponse(
            "photos.html",
            {
                "site_name": site_name,
                "page_title": page_title,
                "page_description": page_description,
                "show_controls": True,
                "album": album,
                "request": request,
            }
        )


# lazy-loads the photos via htmx
@router.get("/photo-albums/{album}")
async def photo_albums(request: Request, album: Optional[str], user: Optional[dict] = Depends(get_user)):
    if user is None:
        # User is not authenticated, redirect to login
        request.session['origin'] = f"/photos/{album}"
        return templates.TemplateResponse(
            "login.html",
            {
                "site_name": "Login",
                "request": request,
            }
        )
    else:
        photos = await load_photos(album)
        return templates.TemplateResponse(
            f"{album}/photos.html",
            {
                "site_name": "Daisy's 40th Birthday - Photos",
                "page_title": "Daisy's 40th Birthday - Photos",
                "page_description": "Photos for Daisy's 40th Birthday",
                "photos": photos,
                "request": request,
            }
        )

async def load_photos(album: str):

    sub_path = f"{album}/processed"
    local_dir = join(settings.PHOTOS_DIR, sub_path)

    photo_files = list_photos_in_dir(local_dir, sub_path)
    if len(photo_files) == 0:

        # nothing saved locally - grab the processed photos from GCS bucket instead
        log.info(f"Downloading photos from GCS [{settings.GCS_BUCKET_NAME}/{sub_path}]")
        client = create_storage_client()
        bucket = client.get_bucket(settings.GCS_BUCKET_NAME)

        blobs = bucket.list_blobs(prefix=sub_path)

        for blob in blobs:
            if valid_photo(blob.name):
                destination_file_name = join(settings.PHOTOS_DIR, blob.name)
                log.debug(f"Downloading {blob.name} to {destination_file_name}")
                blob.download_to_filename(destination_file_name)

    return photo_files


def list_photos_in_dir(directory, sub_path):
    return sorted([join(sub_path, f) for f in listdir(directory) if valid_photo(f)])


def valid_photo(filename):
    if filename.endswith(".jpg") or filename.endswith(".JPG"):
        return True
    return False
