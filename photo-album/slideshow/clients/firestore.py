from google.cloud import firestore
from google.cloud.firestore import Query

from slideshow.config import settings

def create_firestore_client():
    return firestore.Client(project=settings.DATA_PROJECT_ID)
