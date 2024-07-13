from os import listdir

from slideshow.config import settings

async def load_images():
    jpg_files = [f for f in listdir(settings.PHOTOS_DIR) if f.endswith('.jpg')]
    return jpg_files
