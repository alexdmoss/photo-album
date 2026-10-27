import zipfile
from io import BytesIO

from main import app
from photo_album.auth import get_user
from photo_album.config import settings


def test_download_requires_login(client):
    response = client.get("/download", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/login"


def test_download_zips_photos_when_logged_in(client):
    (settings.PHOTOS_DIR / "album").mkdir(exist_ok=True)
    (settings.PHOTOS_DIR / "album" / "photo.jpg").write_bytes(b"jpeg")
    app.dependency_overrides[get_user] = lambda: {"email": "someone@example.com"}

    try:
        response = client.get("/download")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert "album/photo.jpg" in zipfile.ZipFile(BytesIO(response.content)).namelist()
