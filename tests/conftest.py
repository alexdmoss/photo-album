import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Create temporary directories for static files
temp_dir = tempfile.mkdtemp()
temp_static = Path(temp_dir) / "static"
temp_assets = Path(temp_dir) / "assets"
temp_static.mkdir(exist_ok=True)
temp_assets.mkdir(exist_ok=True)

# Mock GCP secret reading before ANY imports that might use it
mock_auth_secret = json.dumps(
    {
        "client-id": "test-client-id",
        "client-secret": "test-client-secret",
        "secret-key": "test-secret-key",
    }
)

# Patch before importing anything that triggers the secret read
with patch(
    "google.cloud.secretmanager.SecretManagerServiceClient"
) as mock_client_class:
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance

    # Mock the response structure
    mock_response = MagicMock()
    mock_response.payload.data = mock_auth_secret.encode("UTF-8")
    mock_response.payload.data_crc32c = 0
    mock_instance.access_secret_version.return_value = mock_response

    # Also patch google_crc32c to avoid checksum validation
    with patch("google_crc32c.Checksum") as mock_crc:
        mock_crc_instance = MagicMock()
        mock_crc_instance.hexdigest.return_value = "0"
        mock_crc.return_value = mock_crc_instance

        # Import config and patch the settings instance before app import
        from photo_album.config import settings

        settings.STATIC_DIR = temp_static
        settings.PHOTOS_DIR = temp_assets

        from main import app


@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client


USER = "alex@example.com"


@pytest.fixture()
def firestore(monkeypatch):
    """In-memory Firestore with two albums: one shared with USER, one not."""
    import photo_album.albums
    import photo_album.auth
    import photo_album.likes
    from tests.fake_firestore import FakeFirestore

    db = FakeFirestore()
    db.add("users", "alex", {"email": USER, "apps": ["photo-album"]})
    db.add("users", "other", {"email": "other@example.com", "apps": ["other-app"]})
    db.add(
        "albums",
        "holiday",
        {
            "Name": "holiday",
            "Title": "Summer Holiday",
            "Type": "photos",
            "Cover": "cover.jpg",
            "AlbumDate": "2026-08-01",
            "Users": [USER],
        },
    )
    db.add(
        "albums",
        "wedding",
        {
            "Name": "wedding",
            "Title": "Wedding Videos",
            "Type": "videos",
            "Cover": "first-dance.mp4",
            "AlbumDate": "2025-06-01",
            "Users": ["other@example.com"],
        },
    )
    for module in (photo_album.albums, photo_album.auth, photo_album.likes):
        monkeypatch.setattr(module, "db_client", db)
    return db


@pytest.fixture()
def logged_in(client, firestore, monkeypatch):
    """Logs USER in for real, through the OAuth callback with Google mocked."""
    from unittest.mock import AsyncMock

    from photo_album.auth import oauth

    token = {"userinfo": {"email": USER}}
    monkeypatch.setattr(
        oauth.google, "authorize_access_token", AsyncMock(return_value=token)
    )
    client.get("/auth/google", follow_redirects=False)


@pytest.fixture()
def photos_on_disk():
    """Files as the gcsfuse mount would present them."""
    holiday = settings.PHOTOS_DIR / "holiday" / "processed"
    holiday.mkdir(parents=True, exist_ok=True)
    for name in ("2026-08-02 beach.jpg", "2026-08-01 airport.jpg", "notes.txt"):
        (holiday / name).write_bytes(b"x")
    wedding = settings.PHOTOS_DIR / "wedding" / "videos"
    wedding.mkdir(parents=True, exist_ok=True)
    for name in ("first-dance.mp4", "speech.mov", "thumbs.db"):
        (wedding / name).write_bytes(b"x")
