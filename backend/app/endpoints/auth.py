from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_current_user
from app.core.database import get_db
from app.models.users import User
from app.schemas.auth import TokenResponse, UserResponse
from app.services.oauth import (
    get_google_auth_url,
    exchange_code_for_user_info,
    get_or_create_user,
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login")
async def google_login():
    url = get_google_auth_url()
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        user_info = await exchange_code_for_user_info(code)
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao autenticar com o Google")

    user = await get_or_create_user(db, user_info)
    token = create_access_token({"sub": str(user.id), "email": user.email})

    return RedirectResponse(
        f"{settings.FRONTEND_URL}/auth/callback?token={token}"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user
