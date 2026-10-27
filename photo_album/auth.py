from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from photo_album.clients.firestore import db_client
from photo_album.logger import log
from photo_album.secret import get_value_from_secret, read_auth_api_secret

oauth = OAuth()

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=get_value_from_secret(read_auth_api_secret(), "client-id"),
    client_secret=get_value_from_secret(read_auth_api_secret(), "client-secret"),
    client_kwargs={"scope": "openid email profile"},
)


def get_user(request: Request) -> dict | None:
    user = request.session.get("user")
    if user is not None:
        return user
    else:
        log.warn("Could not validate credentials - directing towards login")


class LoggedInStaticFiles(StaticFiles):
    """StaticFiles that refuses anyone not logged in.

    The photos bucket is private, but the pod mounts it with its own service
    account, so without this anyone with a file's URL could fetch it.
    """

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and get_user(Request(scope)) is None:
            response = PlainTextResponse("Not logged in", status_code=401)
            await response(scope, receive, send)
            return
        await super().__call__(scope, receive, send)


def is_user_authorised(user):
    allowed_users = get_users_from_firestore()
    if user in allowed_users:
        return True
    else:
        log.warn(f"User not permitted [{user}]")
        raise HTTPException(
            403,
            "Unable to log you in - are you sure you are allowed to access this site?",
        )


def get_users_from_firestore():
    dataset = db_client.collection("users")
    return [
        result.to_dict()["email"]
        for result in dataset.stream()
        if "photo-album" in result.to_dict().get("apps", [])
    ]
