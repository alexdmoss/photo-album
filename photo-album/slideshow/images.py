from os import listdir
from os.path import join

from slideshow.logger import log
from slideshow.clients.storage import create_storage_client
from slideshow.config import settings


async def load_images():

    local_dir = join(settings.PHOTOS_DIR, settings.GCS_BUCKET_PHOTOS_PATH)

    jpg_files = list_images_in_dir(local_dir, ".jpg")
    if len(jpg_files) == 0:

        # nothing saved locally - grab the processed images from GCS bucket instead
        log.info(f"Downloading images from GCS [{settings.GCS_BUCKET_NAME}/{settings.GCS_BUCKET_PHOTOS_PATH}]")
        client = create_storage_client()
        bucket = client.get_bucket(settings.GCS_BUCKET_NAME)

        blobs = bucket.list_blobs(prefix=settings.GCS_BUCKET_PHOTOS_PATH)

        for blob in blobs:
            if blob.name.endswith('.jpg'):
                destination_file_name = join(settings.PHOTOS_DIR, blob.name)
                log.debug(f"Downloading {blob.name} to {destination_file_name}")
                blob.download_to_filename(destination_file_name)

        jpg_files = list_images_in_dir(local_dir, ".jpg")

    return jpg_files


def list_images_in_dir(directory, extension):
    return sorted([join(settings.GCS_BUCKET_PHOTOS_PATH, f) for f in listdir(directory) if f.endswith(extension)])
