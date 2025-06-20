from os import listdir

from PIL import Image

from photo_album.logger import log

PHOTOS_DIR = "../assets/"
ORIGINALS_DIR = "../originals/"


def resize_images():

    log.info("Resizing images")
    jpg_files = [f for f in listdir(ORIGINALS_DIR) if f.endswith('.jpg')]

    images_info = []

    for image_filename in jpg_files:
        with Image.open(f"{ORIGINALS_DIR}/{image_filename}") as img:

            original_width, original_height = img.size

            if original_height < 1024:
                log.warn(f"Image {image_filename} has a lower height resolution than 1024 - padding with black background")

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
                new_img.save(f"{PHOTOS_DIR}/{image_filename}")

                # Update images_info with new image details
                images_info.append(image_filename)

            elif original_height >= 1024:
                aspect_ratio = original_width / original_height
                new_height = 1024
                new_width = int(new_height * aspect_ratio)

                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized_img.save(f"{PHOTOS_DIR}/{image_filename}")

            images_info.append(image_filename)

    return images_info
