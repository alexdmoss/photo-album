from typing import Optional
from os import listdir
from os.path import join

from fastapi import Request, Depends

from photo_album.logger import log
from photo_album.clients.storage import create_storage_client
from photo_album.config import settings
from photo_album.routes import router, templates
from photo_album.auth import get_user
from photo_album.albums import get_album_title, validate_album


@router.get("/videos/{album}")
async def videos(request: Request, album: Optional[str], user: Optional[dict] = Depends(get_user)):

    if validate_album(album) is False:
        log.error(f"Invalid album name: {album}")
        return templates.TemplateResponse(
            "error.html",
            {
                "site_name": "Error",
                "page_title": "Invalid Album",
                "page_description": "The requested album is invalid.",
                "request": request,
            }
        )
    if album is not None:
        page_title = get_album_title(album)
    else:
        page_title = None

    if page_title is None:
        page_title = "Video Albums"
    # @TODO: do something more useful with these fields
    site_name = page_title
    page_description = page_title

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
            "video-album.html",
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

    if validate_album(album) is False:
        log.error(f"Invalid album name: {album}")
        return templates.TemplateResponse(
            "error.html",
            {
                "site_name": "Error",
                "page_title": "Invalid Album",
                "page_description": "The requested album is invalid.",
                "request": request,
            }
        )

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
    elif album is None:
        # Handle missing album parameter
        return templates.TemplateResponse(
            "videos.html",
            {
                "videos": [],
                "request": request,
            }
        )
    else:
        videos = load_videos(album)
        return templates.TemplateResponse(
            "videos.html",
            {
                "videos": videos,
                "request": request,
            }
        )


def load_videos(album: str):

    sub_path = f"{album}/videos"

    local_dir = join(settings.PHOTOS_DIR, sub_path)
    allowed_extensions = [".mp4", ".mkv", ".m4v", ".mov"]

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
    try:
        return sorted([join(sub_path, f) for f in listdir(directory) if any(f.endswith(ext) for ext in extensions)])
    except FileNotFoundError:
        return []
