from pathlib import Path

from photo_album import photos
from photo_album.config import settings


class FakeBlob:
    def __init__(self, name):
        self.name = name

    def download_to_filename(self, filename):
        Path(filename).write_bytes(b"x")


class FakeStorageClient:
    def __init__(self, names):
        self.names = names

    def get_bucket(self, _name):
        return self

    def list_blobs(self, prefix):
        return [FakeBlob(n) for n in self.names if n.startswith(prefix)]


def test_load_photos_downloads_from_gcs_when_nothing_local(monkeypatch):
    (settings.PHOTOS_DIR / "garden" / "processed").mkdir(parents=True, exist_ok=True)
    names = [
        "garden/processed/2026-05-02 roses.jpg",
        "garden/processed/2026-05-01 pond.JPG",
        "garden/processed/readme.txt",
    ]
    monkeypatch.setattr(photos, "create_storage_client", lambda: FakeStorageClient(names))

    assert photos.load_photos("garden") == [
        "garden/processed/2026-05-01 pond.JPG",
        "garden/processed/2026-05-02 roses.jpg",
    ]
