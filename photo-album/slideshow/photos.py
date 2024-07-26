from os import listdir
from os.path import join
from typing import Optional

from fastapi import Request, Depends

from slideshow.clients.storage import create_storage_client
from slideshow.logger import log
from slideshow.config import settings
from slideshow.auth import get_user
from slideshow.routes import router, templates


@router.get("/photos/{album}")
async def daisy(request: Request, album: Optional[str], user: Optional[dict] = Depends(get_user)):
    # @TODO: this should not be hard-coded here
    if album == "daisy":
        site_name = "Daisy's 40th"
        page_title = "Daisy's 40th"
        page_description = "Photos for Daisy's 40th Birthday"
    else:
        site_name = "Photos Albums"
        page_title = "Photos Albums"
        page_description = "Photos Albums"

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

    photo_files = list_photos_in_dir(local_dir, sub_path, ".jpg")
    if len(photo_files) == 0:

        # nothing saved locally - grab the processed photos from GCS bucket instead
        log.info(f"Downloading photos from GCS [{settings.GCS_BUCKET_NAME}/{sub_path}]")
        client = create_storage_client()
        bucket = client.get_bucket(settings.GCS_BUCKET_NAME)

        blobs = bucket.list_blobs(prefix=sub_path)

        for blob in blobs:
            if blob.name.endswith('.jpg'):
                destination_file_name = join(settings.PHOTOS_DIR, blob.name)
                log.debug(f"Downloading {blob.name} to {destination_file_name}")
                blob.download_to_filename(destination_file_name)

        photo_files = list_photos_in_dir(local_dir, sub_path, ".jpg")

    return photo_files


def list_photos_in_dir(directory, sub_path, extension):
    return sorted([join(sub_path, f) for f in listdir(directory) if f.endswith(extension)])