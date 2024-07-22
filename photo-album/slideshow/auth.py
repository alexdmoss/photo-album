from typing import Optional
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth

from slideshow.logger import log
from slideshow.secret import read_auth_api_secret, get_value_from_secret


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
        log.warn(f"Could not validate credentials - directing towards login")
