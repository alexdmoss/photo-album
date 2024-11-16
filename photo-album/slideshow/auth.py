from os import getenv
from typing import Optional

from fastapi import HTTPException
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth

from slideshow.logger import log
from slideshow.secret import read_auth_api_secret, get_value_from_secret
from slideshow.clients.firestore import db_client

oauth = OAuth()

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=get_value_from_secret(read_auth_api_secret(), "client-id"),
    client_secret=get_value_from_secret(read_auth_api_secret(), "client-secret"),
    client_kwargs={
        "scope": "openid email profile"
    }
)


async def get_user(request: Request) -> Optional[dict]:
    user = request.session.get("user")
    if user is not None:
        return user
    else:
        log.warn("Could not validate credentials - directing towards login")


def is_user_authorised(user):
    allowed_users = get_users_from_firestore()
    if user in allowed_users:
        return True
    else:
        log.warn(f"User not permitted [{user}]")
        raise HTTPException(403, "Unable to log you in - are you sure you are allowed to access this site?")


def get_users_from_firestore():
    dataset = db_client.collection("users")
    return [result.to_dict()["email"] for result in dataset.stream() if "photo-album" in result.to_dict().get("apps", [])]
