from typing import Optional
from os import listdir, sep
from os.path import join, normpath, isabs, abspath

from fastapi import Request, Depends

from slideshow.logger import log
from slideshow.clients.storage import create_storage_client
from slideshow.config import settings
from slideshow.routes import router, templates
from slideshow.auth import get_user
from slideshow.albums import get_album_title


@router.get("/videos/{album}")
async def videos(request: Request, album: Optional[str], user: Optional[dict] = Depends(get_user)):

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


def list_videos_in_dir(base_directory, sub_path, extensions):
    # Only allow safe sub_path
    safe_sub_path = normpath(sub_path)
    if isabs(safe_sub_path) or '..' in safe_sub_path.split(sep):
        raise ValueError("Invalid sub_path")
    directory = join(base_directory, safe_sub_path)
    directory = abspath(directory)
    # Ensure directory is within base_directory
    if not directory.startswith(abspath(base_directory)):
        raise ValueError("Directory traversal detected")
    try:
        return sorted([join(safe_sub_path, f) for f in listdir(directory) if any(f.endswith(ext) for ext in extensions)])
    except FileNotFoundError:
        return []
