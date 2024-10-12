from google.cloud import firestore
from google.cloud.firestore import Query

from slideshow.config import settings

def create_firestore_client():
    return firestore.Client(project=settings.GCP_PROJECT_ID)
