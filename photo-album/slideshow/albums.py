import os

from dataclasses import dataclass

from slideshow.clients.firestore import db_client, Query
from slideshow.config import settings
from slideshow.logger import log

ALBUM_COLLECTION = "albums"
ORDER_BY = "AlbumDate"


@dataclass
class Album:
    Name: str
    Title: str
    Type: str
    Cover: str
    ImageCount: int


def get_albums(user: str):

    albums = []
    dataset = db_client.collection(ALBUM_COLLECTION).order_by(ORDER_BY, direction=Query.DESCENDING)
    results = dataset.stream()

    for result in results:
        # filtering client-side rather than with where clause to avoid need for index management
        if user in result.to_dict().get("Users", []):
            album_data = result.to_dict()
            album = Album(
                Name = album_data["Name"],
                Title = album_data["Title"],
                Type = album_data["Type"],
                Cover = album_data["Cover"],
                ImageCount = get_number_of_images(album_data["Name"])
            )
            albums.append(album)

    return albums


def get_album_title(album: str):

    dataset = db_client.collection(ALBUM_COLLECTION)
    docs = dataset.where("Name", "==", album).stream()
    for doc in docs:
        return doc.to_dict().get("Title")
    return None


# def get_number_of_images(album: str):
#     client = create_storage_client()
#     bucket = client.get_bucket(settings.GCS_BUCKET_NAME)
#     prefix = f"{album}/processed/"
#     blobs = bucket.list_blobs(prefix=prefix)
#     return sum(1 for _ in blobs)


def get_number_of_images(album: str):
    album_path = os.path.join(settings.PHOTOS_DIR, album, "processed")
    image_count = 0

    try:
        for _ in os.listdir(album_path):
            image_count += 1
    except FileNotFoundError:
        log.warn(f"Error counting files in album directory [{album_path}]. Does it exist?")

    return image_count