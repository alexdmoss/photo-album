import os
import re

from dataclasses import dataclass

from slideshow.clients.firestore import db_client, FIRESTORE_QUERY
from slideshow.config import settings
from slideshow.logger import log

ALBUM_COLLECTION = "albums"
ORDER_BY = "AlbumDate"


@dataclass
class Album:
    name: str
    title: str
    type: str
    cover: str
    image_count: int


def get_albums(user: str):

    albums = []
    dataset = db_client.collection(ALBUM_COLLECTION).order_by(ORDER_BY, direction=FIRESTORE_QUERY.DESCENDING)
    results = dataset.stream()

    for result in results:
        # filtering client-side rather than with where clause to avoid need for index management
        if user in result.to_dict().get("Users", []):
            album_data = result.to_dict()
            album = Album(
                name=album_data["Name"],
                title=album_data["Title"],
                type=album_data["Type"],
                cover=album_data["Cover"],
                image_count=get_number_of_assets(album_name=album_data["Name"], album_type=album_data["Type"])
            )
            albums.append(album)

    return albums


def get_album_title(album: str):

    dataset = db_client.collection(ALBUM_COLLECTION)
    docs = dataset.where("Name", "==", album).stream()
    for doc in docs:
        return doc.to_dict().get("Title")
    return None


def get_number_of_assets(album_name: str, album_type: str):
    if album_type == "photos":
        sub_path = "processed"
    else:
        sub_path = "videos"
    album_path = os.path.join(settings.PHOTOS_DIR, album_name, sub_path)
    image_count = 0

    try:
        for _ in os.listdir(album_path):
            image_count += 1
    except FileNotFoundError:
        log.warn(f"Error counting files in album directory [{album_path}]. Does it exist?")

    return image_count


def validate_album(album):
    # Allow only alphanumeric, underscore, hyphen; 1-50 chars
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,50}', album):
        raise ValueError("Invalid album name")
    return album
