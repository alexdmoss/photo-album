from slideshow.clients.firestore import db_client, Query

ALBUM_COLLECTION = "albums"
ORDER_BY = "AlbumDate"


def get_albums():
    dataset = db_client.collection(ALBUM_COLLECTION)
    query = dataset.order_by(ORDER_BY, direction=Query.DESCENDING)
    results = query.stream()
    return [result.to_dict() for result in results]
