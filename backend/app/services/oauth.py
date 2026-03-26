import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import settings
from app.models.users import User as UserModel


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


def get_google_auth_url(state: str = "") -> str:
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def exchange_code_for_user_info(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_resp.raise_for_status()
        tokens = token_resp.json()

        user_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        user_resp.raise_for_status()
        return user_resp.json()


async def get_or_create_user(db: AsyncSession, user_info: dict):
    result = await db.execute(
        select(UserModel).where(UserModel.google_id == user_info["id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        result = await db.execute(
            select(UserModel).where(UserModel.email == user_info["email"])
        )
        user = result.scalar_one_or_none()

    if user:
        user.google_id = user_info["id"]
        user.name = user_info.get("name", user.name)
    else:
        user = UserModel(
            email=user_info["email"],
            name=user_info.get("name", ""),
            google_id=user_info["id"],
        )
        db.add(user)

    await db.flush()
    await db.refresh(user)
    return user
