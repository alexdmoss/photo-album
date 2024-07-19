import logging
import logging.config

from os import listdir
from os.path import join

from slideshow.clients.storage import create_storage_client
from slideshow.config import settings


logging.config.fileConfig(f"{settings.APP_DIR}/../logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


async def load_images():
    # we've already been to get the images from GCS, don't re-download them
    jpg_files = list_images_in_dir(settings.PHOTOS_DIR, ".jpg")
    if len(jpg_files) == 0:
        # nothing saved locally - grab the processed images from GCS bucket instead
        logging.info(f"Downloading images from GCS [{settings.GCS_BUCKET_NAME}/{settings.GCS_BUCKET_PATH}]")
        client = create_storage_client()
        bucket = client.get_bucket(settings.GCS_BUCKET_NAME)

        # List all objects in the bucket and download images
        blobs = bucket.list_blobs(prefix=settings.GCS_BUCKET_PATH, delimiter='/')
        for blob in blobs:
            if blob.name.endswith('.jpg'):
                destination_file_name = join(settings.PHOTOS_DIR, blob.name.split('/')[-1])
                blob.download_to_filename(destination_file_name)

        jpg_files = list_images_in_dir(settings.PHOTOS_DIR, ".jpg")

    return jpg_files


def list_images_in_dir(directory, extension):
    return sorted([f for f in listdir(directory) if f.endswith(extension)])
