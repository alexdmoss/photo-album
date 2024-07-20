from os import getenv
import jwt
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from slideshow.secret import AUTH_CREDS, get_value_from_secret

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# @TODO: Create a fake db:
FAKE_DB = {'alex@alexos.dev': {'name': 'Alex M'}}

API_SECRET_KEY = get_value_from_secret(AUTH_CREDS, "api-secret-key") or None
if API_SECRET_KEY is None:
    raise ValueError("Missing API_SECRET_KEY")
API_ALGORITHM = getenv('API_ALGORITHM') or 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)


def decode_token(token):
    return jwt.decode(token, API_SECRET_KEY, algorithms=[API_ALGORITHM])


def valid_email_from_db(email):
    return email in FAKE_DB


async def get_current_user_email(token: str = Depends(oauth2_scheme)):

    try:
        payload = decode_token(token)
        email: str = payload.get('sub')
        if email is None:
            logger.error(f"Token email is empty [{CREDENTIALS_EXCEPTION}]")
            raise CREDENTIALS_EXCEPTION
    except jwt.PyJWTError as e:
        logger.error(f"Token JWT Error [{e}]")
        raise CREDENTIALS_EXCEPTION from e

    if valid_email_from_db(email):
        return email

    raise CREDENTIALS_EXCEPTION
