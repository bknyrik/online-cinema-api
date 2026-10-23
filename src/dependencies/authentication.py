from __future__ import annotations
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer

from dependencies import database, services
from src.database.models import accounts as models
from src.repositories import accounts as repositories


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
    db: database.AsyncSessionDep,
    jwt_auth_service: services.JWTAuthServiceDep,
    token: str = Depends(oauth2_scheme)
) -> models.UserModel:
    user_repository = repositories.UserRepository()
    payload = jwt_auth_service.decode_token(token)

    user = await user_repository.aget_by_id(
        db=db,
        id_=int(payload["sub"]),
        join_relationships=["profile", "group"]
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


async def get_current_admin(current_user: CurrentUserDep) -> models.UserModel:
    if current_user.group.name.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an admin to perform this action"
        )

    return current_user


async def get_current_moderator_or_admin(
    current_user: CurrentUserDep
) -> models.UserModel:
    if current_user.group.name not in ("moderator", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a moderator/admin to perform this action"
        )

    return current_user


CurrentUserDep = Annotated[models.UserModel, Depends(get_current_user)]
CurrentAdminDep = Annotated[models.UserModel, Depends(get_current_admin)]
CurrentModeratorOrAdminDep = Annotated[
    models.UserModel, Depends(get_current_moderator_or_admin)
]
