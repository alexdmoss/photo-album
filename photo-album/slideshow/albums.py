from slideshow.clients.firestore import db_client, Query

ALBUM_COLLECTION = "albums"
ORDER_BY = "AlbumDate"


def get_albums(user: str):

    albums = []
    dataset = db_client.collection(ALBUM_COLLECTION).order_by(ORDER_BY, direction=Query.DESCENDING)
    results = dataset.stream()
    # filtering client-side rather than with where clause to avoid need for index management
    return [result.to_dict() for result in results if user in result.to_dict().get("Users", [])]
