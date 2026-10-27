"""Every page and htmx fragment, logged in and out, against fake Firestore."""

from unittest.mock import AsyncMock

import pytest

from photo_album.auth import oauth
from photo_album.routes import format_caption
from tests.conftest import USER


def test_home_lists_only_albums_shared_with_user(
    client, firestore, logged_in, photos_on_disk
):
    response = client.get("/")
    assert response.status_code == 200
    assert f"Welcome back {USER}" in response.text
    # the count is of every file in the folder, so notes.txt is included
    assert "Summer Holiday (3)" in response.text
    assert "/assets/holiday/processed/cover.jpg" in response.text
    assert "Wedding Videos" not in response.text


@pytest.mark.parametrize(
    "page",
    [
        "/photos/holiday",
        "/photo-albums/holiday",
        "/videos/wedding",
        "/video-albums/wedding",
    ],
)
def test_album_pages_ask_logged_out_users_to_log_in(client, firestore, page):
    response = client.get(page)
    assert response.status_code == 200
    assert "click here to log in" in response.text
    assert "/assets/" not in response.text


@pytest.mark.parametrize(
    "page", ["/photos/no-such-album", "/photos/bad..name", "/videos/no-such-album"]
)
def test_unknown_or_invalid_album_shows_error(client, firestore, logged_in, page):
    response = client.get(page)
    assert response.status_code == 200
    assert "Invalid Album" in response.text


def test_photo_album_page(client, firestore, logged_in):
    response = client.get("/photos/holiday")
    assert response.status_code == 200
    assert "<title>Summer Holiday" in response.text
    assert 'hx-get="/photo-albums/holiday"' in response.text


def test_photo_album_fragment_lists_photos_in_order(
    client, firestore, logged_in, photos_on_disk
):
    response = client.get("/photo-albums/holiday")
    assert response.status_code == 200
    airport = response.text.index(
        'data-src="/assets/holiday/processed/2026-08-01 airport.jpg"'
    )
    beach = response.text.index(
        'data-src="/assets/holiday/processed/2026-08-02 beach.jpg"'
    )
    assert airport < beach
    assert "notes.txt" not in response.text
    assert "01/08/2026: airport" in response.text


def test_video_album_fragment_lists_videos(
    client, firestore, logged_in, photos_on_disk
):
    response = client.get("/video-albums/wedding")
    assert response.status_code == 200
    assert "/assets/wedding/videos/first-dance.mp4" in response.text
    assert "/assets/wedding/videos/speech.mov" in response.text
    assert "thumbs.db" not in response.text


def test_like_creates_then_increments(client, firestore, logged_in):
    assert client.post("/likes/holiday/beach.jpg").status_code == 200
    response = client.post("/likes/holiday/beach.jpg")
    assert response.status_code == 200
    assert "fa-heart" in response.text
    like = firestore.collections["likes"]["holiday-beach.jpg"]
    assert like["Likes"] == 2
    assert like["Users"] == [USER]


def test_like_requires_login(client, firestore):
    response = client.post("/likes/holiday/beach.jpg")
    assert "click here to log in" in response.text
    assert "likes" not in firestore.collections


def test_login_callback_lets_allowed_user_in(client, logged_in):
    # logged_in has just been through /auth/google; the session carries the user
    assert f"Welcome back {USER}" in client.get("/").text
    client.get("/logout")
    assert "Welcome back" not in client.get("/").text


def test_login_callback_refuses_user_without_the_app(client, firestore, monkeypatch):
    token = {"userinfo": {"email": "other@example.com"}}
    monkeypatch.setattr(
        oauth.google, "authorize_access_token", AsyncMock(return_value=token)
    )

    response = client.get("/auth/google")
    assert response.status_code == 403
    assert "are you sure you are allowed" in response.text
    assert "Welcome back" not in client.get("/").text


@pytest.mark.parametrize(
    "path, caption",
    [
        ("album/2026-08-01 beach.jpg", "01/08/2026: beach"),
        ("album/2026.08.01_beach.jpg", "01/08/2026: beach"),
        ("album/2026-13-01 bad month.jpg", "2026-13-01 bad month"),
        ("album/IMG_0001.JPG", "IMG_0001"),
    ],
)
def test_format_caption(path, caption):
    assert format_caption(path) == caption
