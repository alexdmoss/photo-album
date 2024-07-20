import json
import logging
from os import getenv

from google.cloud import secretmanager
import google_crc32c

GCP_PROJECT_ID = getenv("GCP_PROJECT_ID")
SECRET_ID = "auth-api"

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def secret_manager_client():
    return secretmanager.SecretManagerServiceClient()


def read_auth_api_secret():

    client = secret_manager_client()
    name = f"projects/{GCP_PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"

    response = client.access_secret_version(request={"name": name})

    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        logger.error(f"Data corruption detected in secret [{SECRET_ID}]")
        return response

    payload = response.payload.data.decode("UTF-8")
    return payload


AUTH_CREDS = read_auth_api_secret()


def get_value_from_secret(secret_payload, key):
    payload = json.loads(secret_payload)
    return (payload[key])
