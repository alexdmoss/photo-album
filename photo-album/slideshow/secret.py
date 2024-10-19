import json

from google.cloud import secretmanager
import google_crc32c

from slideshow.logger import log
from slideshow.config import settings


def secret_manager_client():
    return secretmanager.SecretManagerServiceClient()


def read_auth_api_secret():

    client = secret_manager_client()
    name = f"projects/{settings.DATA_PROJECT_ID}/secrets/{settings.AUTH_SECRET_ID}/versions/latest"

    response = client.access_secret_version(request={"name": name})

    # check secret not tampered with
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        log.error(f"Data corruption detected in secret [{settings.AUTH_SECRET_ID}]")
        return response

    payload = response.payload.data.decode("UTF-8")
    return payload


AUTH_CREDS = read_auth_api_secret()


def get_value_from_secret(secret_payload, key):
    payload = json.loads(secret_payload)
    return (payload[key])
