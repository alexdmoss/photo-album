from google.cloud import firestore
from google.cloud.firestore import Query

from slideshow.config import settings
from slideshow.logger import log

log.info("Instantiating Firestore DB Client")
db_client = firestore.Client(project=settings.DATA_PROJECT_ID)
