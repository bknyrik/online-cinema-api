from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.security.auth import decode_access_token
from dependencies.dependencies import get_db
from src.database.models.accounts import UserModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserModel:
    payload = decode_access_token(token)

    result = await db.execute(
        select(UserModel)
        .options(joinedload(UserModel.group))
        .where(UserModel.email == payload["sub"])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


async def require_admin_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if current_user.group.name.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an admin to perform this action"
        )

    return current_user
