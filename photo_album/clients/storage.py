from google.cloud import storage


def create_storage_client():
    return storage.Client()
