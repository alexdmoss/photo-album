from google.cloud import firestore
from google.cloud.firestore import Query

from photo_album.config import settings
from photo_album.logger import log

FIRESTORE_QUERY = Query

log.info("Instantiating Firestore DB Client")
db_client = firestore.Client(project=settings.DATA_PROJECT_ID)
