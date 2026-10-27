from photo_album.config import settings


def _photo():
    (settings.PHOTOS_DIR / "album" / "processed").mkdir(parents=True, exist_ok=True)
    (settings.PHOTOS_DIR / "album" / "processed" / "photo.jpg").write_bytes(b"jpeg")


def test_assets_require_login(client):
    _photo()
    response = client.get("/assets/album/processed/photo.jpg")
    assert response.status_code == 401
    assert response.content != b"jpeg"


def test_assets_served_when_logged_in(client, logged_in):
    _photo()
    response = client.get("/assets/album/processed/photo.jpg")
    assert response.status_code == 200
    assert response.content == b"jpeg"
