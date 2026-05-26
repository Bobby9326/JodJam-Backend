from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyCookie
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.modules.auths.auth_repository import AuthRepository
from app.modules.auths.auth_service import AuthService
from app.modules.auths.auth_schema import LoginResponse, MeResponse, TokenRefreshResponse, LogoutResponse
from authlib.integrations.starlette_client import OAuth


ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter(tags=["auth"])

# COOKIE SCHEMES
access_cookie = APIKeyCookie(name="access_token", auto_error=False)
refresh_cookie = APIKeyCookie(name="refresh_token", auto_error=False)

# OAUTH
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# DEPENDENCY
def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    repo = AuthRepository(session)
    return AuthService(repo)


# LOGIN GOOGLE
@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = "http://localhost:8000/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


# GOOGLE CALLBACK
@router.get("/auth/google/callback")
async def auth_google_callback(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Cannot get user info")

    user, access_token, refresh_token = auth_service.handle_google_login(user_info)

    response = JSONResponse({
        "message": "login success",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "picture": user.profile_url,
        },
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return response


# REFRESH
@router.post("/refresh")
async def refresh(
    refresh_token: str = Depends(refresh_cookie),
    auth_service: AuthService = Depends(get_auth_service),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        access_token = auth_service.handle_refresh(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    response = JSONResponse({"message": "token refreshed"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


# ME
@router.get("/me")
async def me(access_token: str = Depends(access_cookie)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not logged in")

    try:
        from app.modules.auths.auth_service import AuthService as _AS
        import jwt as _jwt
        payload = _jwt.decode(
            access_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "username": payload.get("username"),
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# LOGOUT
@router.post("/logout")
async def logout(
    refresh_token: str = Depends(refresh_cookie),
    auth_service: AuthService = Depends(get_auth_service),
):
    auth_service.handle_logout(refresh_token)

    response = JSONResponse({"message": "logout success"})
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response
