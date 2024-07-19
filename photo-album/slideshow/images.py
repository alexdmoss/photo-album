from os import listdir
from os.path import join

from PIL import Image

from slideshow.clients.storage import create_storage_client
from slideshow.config import settings

async def load_images():
    # we've already been to get the images from GCS, don't re-download them
    jpg_files = list_images_in_dir(settings.TMP_DIR, ".jpg")
    if len(jpg_files) == 0:
        # nothing saved locally - grab the processed images from GCS bucket instead
        print(f"-> [INFO] Downloading images from GCS [{settings.GCS_BUCKET_NAME}/{settings.GCS_BUCKET_PATH}]")
        client = create_storage_client()
        bucket = client.get_bucket(settings.GCS_BUCKET_NAME)

        # List all objects in the bucket and download images
        blobs = bucket.list_blobs(prefix=settings.GCS_BUCKET_PATH, delimiter='/')
        for blob in blobs:
            print(blob)
            if blob.name.endswith('.jpg'):
                destination_file_name = join(settings.TMP_DIR, blob.name.split('/')[-1])
                blob.download_to_filename(destination_file_name)
                print(f"Downloaded {blob.name} to {destination_file_name}")

        jpg_files = list_images_in_dir(settings.TMP_DIR, ".jpg")

    return jpg_files


def list_images_in_dir(directory, extension):
    return sorted([f for f in listdir(directory) if f.endswith(extension)])


async def resize_images():

    print("-> [INFO] Resizing images")
    jpg_files = [f for f in listdir(settings.PHOTOS_DIR) if f.endswith('.jpg')]

    images_info = []
    
    for image_filename in jpg_files:
        with Image.open(f"{settings.PHOTOS_DIR}/{image_filename}") as img:

            original_width, original_height = img.size

            if original_height < 1024:
                print(f"-> [WARN] Image {image_filename} has a lower height resolution than 1024 - padding with black background")
                
                # Calculate padding to add to top and bottom to reach 1024 height
                padding_top_bottom = (1024 - img.size[1]) // 2
                padding_left_right = 0  # Assuming we only want to adjust the height
                
                # Create a new image with a black background
                new_img = Image.new("RGB", (img.width, 1024), "black")
                
                # Calculate position to paste the original image on the new image
                paste_position = (padding_left_right, padding_top_bottom)
                
                # Paste the original image onto the new image
                new_img.paste(img, paste_position)
                
                # Optionally save the new image or just update the info
                new_img.save(f"{settings.TMP_DIR}/{image_filename}")
                
                # Update images_info with new image details
                images_info.append(image_filename)

            elif original_height >= 1024:
                aspect_ratio = original_width / original_height
                new_height = 1024
                new_width = int(new_height * aspect_ratio)

                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized_img.save(f"{settings.TMP_DIR}/{image_filename}")

            images_info.append(image_filename)

    return images_info
