import jwt
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie

from app.core.config import settings

access_cookie = APIKeyCookie(name="access_token", auto_error=False)
refresh_cookie = APIKeyCookie(name="refresh_token", auto_error=False)


def get_current_payload(access_token: str = Depends(access_cookie)) -> dict:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not logged in")
    try:
        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user_id(payload: dict = Depends(get_current_payload)) -> str:
    return payload["sub"]