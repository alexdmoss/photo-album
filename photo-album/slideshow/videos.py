from typing import Optional
from os import listdir
from os.path import join

from fastapi import Request, Depends

from slideshow.logger import log
from slideshow.clients.storage import create_storage_client
from slideshow.config import settings
from slideshow.routes import router, templates
from slideshow.auth import get_user


@router.get("/videos/{album}")
async def videos(request: Request, album: Optional[str], user: Optional[dict] = Depends(get_user)):

    # @TODO: this should not be hard-coded here
    if album == "daisy":
        site_name = "Videos - Daisy's 40th"
        page_title = "Videos - Daisy's 40th"
        page_description = "Videos for Daisy's 40th Birthday"
    else:
        site_name = "Video Albums"
        page_title = "Video Albums"
        page_description = "Video Albums"

    if user is None:
        # User is not authenticated, redirect to login
        request.session['origin'] = f"/videos/{album}"
        return templates.TemplateResponse(
            "login.html",
            {
                "site_name": "Login",
                "request": request,
            }
        )
    else:
        return templates.TemplateResponse(
            "videos.html",
            {
                "site_name": site_name,
                "page_title": page_title,
                "page_description": page_description,
                "show_controls": False,
                "album": album,
                "request": request,
            }
        )


@router.get("/video-albums/{album}")
async def video_albums(request: Request, album: Optional[str], user: Optional[dict] = Depends(get_user)):
    videos = await load_videos(album)
    if user is None:
        # User is not authenticated, redirect to login
        request.session['origin'] = f"/videos/{album}"
        return templates.TemplateResponse(
            "login.html",
            {
                "site_name": "Login",
                "request": request,
            }
        )
    else:
        return templates.TemplateResponse(
            f"{album}/videos.html",
            {
                "site_name": "Daisy's 40th Birthday - Videos",
                "page_title": "Daisy's 40th Birthday - Videos",
                "page_description": "Videos for Daisy's 40th Birthday",
                "videos": videos,
                "request": request,
            }
        )


async def load_videos(album: str):

    sub_path = f"{album}/videos"

    local_dir = join(settings.PHOTOS_DIR, sub_path)
    allowed_extensions = [".mp4", ".mkv", ".m4v"]

    video_files = list_videos_in_dir(local_dir, sub_path, allowed_extensions)
    if len(video_files) == 0:

        # nothing saved locally - grab the processed images from GCS bucket instead
        log.info(f"Downloading images from GCS [{settings.GCS_BUCKET_NAME}/{sub_path}]")
        client = create_storage_client()
        bucket = client.get_bucket(settings.GCS_BUCKET_NAME)

        blobs = bucket.list_blobs(prefix=sub_path)

        for blob in blobs:
            if any(blob.name.endswith(ext) for ext in allowed_extensions):
                destination_file_name = join(settings.PHOTOS_DIR, blob.name)
                log.debug(f"Downloading {blob.name} to {destination_file_name}")
                blob.download_to_filename(destination_file_name)

        video_files = list_videos_in_dir(local_dir, sub_path, allowed_extensions)

    return video_files


def list_videos_in_dir(directory, sub_path, extensions):
    return sorted([join(sub_path, f) for f in listdir(directory) if any(f.endswith(ext) for ext in extensions)])


