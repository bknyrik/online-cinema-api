from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from src.database.models.accounts import UserModel
from src.repositories.accounts import UserRepository
from src.services.security import JWTAuthService
from src.dependencies.services import get_jwt_auth_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    jwt_auth_service: JWTAuthService = Depends(get_jwt_auth_service)
) -> UserModel:
    user_repository = UserRepository()
    payload = jwt_auth_service.decode_token(token)

    user = await user_repository.aget_with_group_by_id(
        db=db,
        id_=int(payload["sub"])
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


async def get_current_admin_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if current_user.group.name.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an admin to perform this action"
        )

    return current_user


async def get_current_moderator_or_admin_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if current_user.group.name not in ("moderator", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a moderator/admin to perform this action"
        )

    return current_user
