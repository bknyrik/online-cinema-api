from __future__ import annotations
from datetime import datetime, timezone

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from boto3.exceptions import Boto3Error

from src.database.models import accounts as models
from src.services import mixins
from src.services.security import PasswordSecurityService, JWTAuthService
from src.services.celery_beat import CeleryBeatService
from src.services.email_sender import EmailSenderService
from src.services.s3 import S3Service
from src.repositories import accounts as repositories
from src.settings import settings


class UserService(mixins.ModelItemsMixin):

    def __init__(self) -> None:
        self.model_type = models.UserModel
        self.user_repository = repositories.UserRepository()
        self.user_group_repository = repositories.UserGroupRepository()
        self.at_repository = repositories.TokenRepository(
            models.ActivationTokenModel
        )
        self.rt_repository = repositories.TokenRepository(
            models.RefreshTokenModel
        )
        self.prt_repository = repositories.TokenRepository(
            models.PasswordResetTokenModel
        )

    @staticmethod
    def validate_token_is_invalid(
        token_instance: models.AbstractTokenModel | None,
        token_type: str,
        compare_token: str | None = None
    ) -> None:
        if (
            not token_instance
            or (
                compare_token is not None
                and token_instance.token != compare_token
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{token_type} token is invalid"
            )

    @staticmethod
    def validate_token_has_expired(
        token_instance: models.AbstractTokenModel,
        token_type: str
    ) -> None:
        if token_instance.has_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{token_type} token has expired"
            )

    @staticmethod
    def validate_refresh_token_has_valid_type(
        token_instance: models.RefreshTokenModel,
        valid_token_type: str,
        jwt_auth_service: JWTAuthService,
    ) -> None:
        payload = jwt_auth_service.decode_token(token_instance.token)

        if payload["token_type"] != valid_token_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Refresh token must be '{valid_token_type}' type"
            )

    @staticmethod
    def validate_user_is_active(user: models.UserModel) -> None:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is not activated"
            )

    @staticmethod
    def validate_user_is_not_active(user: models.UserModel) -> None:
        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is activated"
            )

    async def register_user(
        self,
        db: AsyncSession,
        data: dict,
        pss: PasswordSecurityService,
        email_sender_service: EmailSenderService,
        background_tasks: BackgroundTasks
    ) -> models.UserModel:
        try:
            user = await self.user_repository.aget_by(
                db=db,
                expressions=[self.model_type.email == data["email"]]
            )

            self.validate_item_by_attrs_exists(
                item=user,
                attrs={"email": data["email"]},
                item_type="User"
            )

            group = await self.user_group_repository.aget_by(
                db=db,
                expressions=[models.UserGroupModel.name == "USER"]
            )

            data["group_id"] = group.id
            data["hashed_password"] = pss.hash_password(data.pop("password"))

            user = await self.user_repository.acreate(db, data)

            activation_token = await self.at_repository.acreate(
                db=db,
                data={
                    "user_id": user.id,
                    "token": self.at_repository.generate_token(),
                }
            )

            background_tasks.add_task(
                email_sender_service.send_activation_email,
                user.email,
                settings.LINK_ACCOUNT_ACTIVATION,
                activation_token.token
            )
            background_tasks.add_task(
                CeleryBeatService.create_periodic_task_to_delete_activation_token,
                user.id,
                activation_token.expires_at
            )

            await db.commit()
            return user
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while user registration"
            )

    async def activate_user_account(
        self,
        data: dict,
        db: AsyncSession
    ) -> dict:
        try:
            user = await self.user_repository.aget_by(
                db=db,
                join_relationships=["activation_token"],
                expressions=[self.model_type.email == data["email"]]
            )

            self.validate_item_by_attrs_not_found(
                item=user,
                attrs={"email": data["email"]},
                item_type="User"
            )

            self.validate_user_is_not_active(user)

            self.validate_token_is_invalid(
                token_instance=user.activation_token,
                token_type="Activation",
                compare_token=data["activation_token"]
            )
            self.validate_token_has_expired(
                token_instance=user.activation_token,
                token_type="Activation"
            )

            await self.user_repository.aupdate(
                db=db,
                instance=user,
                data={"is_active": True}
            )
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while account activation"
            )

        return {"message": "Your account is activated"}

    async def reactivate_user_account(
        self,
        data: dict,
        db: AsyncSession,
        background_tasks: BackgroundTasks,
        email_sender_service: EmailSenderService
    ) -> dict:
        try:
            user = await self.user_repository.aget_by(
                db=db,
                join_relationships=["activation_token"],
                expressions=[self.model_type.email == data["email"]]
            )

            self.validate_item_by_attrs_not_found(
                item=user,
                attrs=data,
                item_type="User"
            )

            token = self.at_repository.generate_token()

            if not user.activation_token:
                user.activation_token = await self.at_repository.acreate(
                    db=db,
                    data={"user_id": user.id, "token": token}
                )
            else:
                user.activation_token.token = token

            await db.commit()

            background_tasks.add_task(
                email_sender_service.send_activation_email,
                user.email,
                settings.LINK_ACCOUNT_ACTIVATION,
                user.activation_token.token
            )

            return {"message": "An activation link is sent to your email"}
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while activating account"
            )

    async def login_for_access_token(
        self,
        data: dict,
        db: AsyncSession,
        jwt_auth_service: JWTAuthService
    ) -> dict:
        try:
            user = await self.user_repository.aget_by(
                db=db,
                expressions=[models.UserModel.email == data["email"]]
            )

            access_token = jwt_auth_service.encode_token(user.id, "access")
            return {"access_token": access_token, "token_type": "Bearer"}
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while login for access token"
            )

    async def login(
        self,
        data: dict,
        pss: PasswordSecurityService,
        jwt_auth_service: JWTAuthService,
        db: AsyncSession,
    ) -> dict:
        user = await self.user_repository.aget_by(
            db=db,
            expressions=[self.model_type.email == data["email"]]
        )

        if (
            not user
            or not pss.verify_password(data["password"], user.hashed_password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid account with given credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is not activated"
            )

        try:
            access_token = jwt_auth_service.encode_token(
                user_id=user.id,
                token_type="access"
            )
            refresh_token = jwt_auth_service.encode_token(
                user_id=user.id,
                token_type="refresh"
            )
            token_instance = await self.rt_repository.acreate(
                db=db,
                data={
                    "user_id": user.id,
                    "token": refresh_token,
                    "expires_at": self.rt_repository.get_expiration_date()
                }
            )

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while login"
            )

        return {
            "access_token": access_token,
            "refresh_token": token_instance.token
        }

    async def logout(
        self,
        db: AsyncSession,
        jwt_auth_service: JWTAuthService,
        data: dict,
        current_user: models.UserModel
    ) -> None:
        try:
            self.validate_user_is_active(current_user)

            token_instance = await self.rt_repository.aget_by(
                db=db,
                expressions=[
                    models.RefreshTokenModel.token == data["refresh_token"]
                ]
            )

            self.validate_token_is_invalid(token_instance, "Refresh")
            self.validate_refresh_token_has_valid_type(
                token_instance=token_instance,
                valid_token_type="refresh",
                jwt_auth_service=jwt_auth_service
            )

            await self.rt_repository.adelete(
                db=db,
                instance=token_instance
            )
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while logout"
            )

    async def change_user_group(
        self,
        db: AsyncSession,
        data: dict,
        user_id: int
    ) -> models.UserModel:
        try:
            group = await self.user_group_repository.aget_by(
                db=db,
                expressions=[models.UserGroupModel.name == data["group"]]
            )

            self.validate_item_by_attrs_not_found(
                item=group,
                attrs=data,
                item_type="Group"
            )

            user = await self.user_repository.aget_by_id(
                db=db,
                id_=user_id,
                join_relationships=["group"]
            )

            self.validate_item_by_id_not_found(
                item=user,
                id_=user_id,
                item_type="User"
            )

            await self.user_repository.aupdate(
                db=db,
                instance=user,
                data={"group_id": group.id}
            )
            user.group = group

            await db.commit()

            return user
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while changing user group"
            )

    async def admin_activate_user_account(
        self,
        user_id: int,
        db: AsyncSession,
    ) -> dict:
        try:
            user = await self.user_repository.aget_by_id(
                db=db,
                id_=user_id
            )

            self.validate_item_by_id_not_found(
                item=user,
                id_=user_id,
                item_type="User"
            )

            self.validate_user_is_not_active(user)

            await self.user_repository.aupdate(
                db=db,
                instance=user,
                data={"is_active": True}
            )
            await db.commit()

            return {"message": "Account is activated successfully"}
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while account activation"
            )

    async def change_user_password(
        self,
        db: AsyncSession,
        data: dict,
        current_user: models.UserModel,
        pss: PasswordSecurityService
    ) -> dict:
        try:
            password_is_verified = pss.verify_password(
                raw_password=data["old_password"],
                hashed_password=current_user.hashed_password
            )

            if not password_is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The old password is invalid"
                )

            await self.user_repository.aupdate(
                db=db,
                instance=current_user,
                data={
                    "hashed_password": pss.hash_password(data["new_password"])
                }
            )
            await db.commit()

            return {"message": "Password is changed successfully"}
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while changing user password"
            )

    async def refresh_access_token(
        self,
        data: dict,
        jwt_auth_service: JWTAuthService,
        db: AsyncSession
    ) -> dict:
        try:
            user = await self.user_repository.aget_by(
                db=db,
                expressions=[self.model_type.email == data["email"]]
            )

            self.validate_item_by_attrs_not_found(
                item=user,
                attrs={"email": data["email"]},
                item_type="User"
            )

            token_instance = await self.rt_repository.aget_by(
                db=db,
                expressions=[
                    models.RefreshTokenModel.token == data["refresh_token"]
                ]
            )

            self.validate_token_is_invalid(
                token_instance=token_instance,
                token_type="Refresh",
            )

            self.validate_token_has_expired(
                token_instance=token_instance,
                token_type="Refresh",
            )

            return {
                "access_token": jwt_auth_service.encode_token(
                    user_id=user.id,
                    token_type="access"
                )
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while refreshing access token"
            )

    async def reset_password(
        self,
        db: AsyncSession,
        data: dict,
        ess: EmailSenderService,
        background_tasks: BackgroundTasks
    ) -> dict:
        try:
            user = await self.user_repository.aget_by(
                db=db,
                expressions=[self.model_type.email == data["email"]]
            )

            if user and user.is_active:
                token_data = {
                    "token": self.prt_repository.generate_token(),
                    "expires_at": self.prt_repository.get_expiration_date()
                }

                token_instance = await self.prt_repository.aget_by(
                    db=db,
                    expressions=[
                        models.PasswordResetTokenModel.user_id == user.id
                    ]
                )

                if not token_instance:
                    token_data["user_id"] = user.id
                    token_instance = await self.prt_repository.acreate(
                        db=db,
                        data=token_data
                    )
                else:
                    await self.prt_repository.aupdate_by(
                        db=db,
                        expressions=[
                            models.PasswordResetTokenModel.user_id == user.id
                        ],
                        data=token_data
                    )

                await db.commit()

                background_tasks.add_task(
                    ess.send_reset_password_email,
                    user.email,
                    settings.LINK_RESET_PASSWORD,
                    token_instance.token
                )

            return {
                "message": (
                    "If you are registered, "
                    "you will receive an email with information"
                )
            }
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while resetting user password"
            )

    async def reset_password_complete(
        self,
        db: AsyncSession,
        data: dict,
        pss: PasswordSecurityService
    ) -> dict:
        try:
            user = await self.user_repository.aget_by(
                db=db,
                expressions=[self.model_type.email == data["email"]]
            )

            self.validate_item_by_attrs_not_found(
                item=user,
                item_type="User",
                attrs={"email": data["email"]}
            )

            token_instance = await self.prt_repository.aget_by(
                db=db,
                expressions=[models.PasswordResetTokenModel.user_id == user.id]
            )

            self.validate_token_is_invalid(
                token_instance=token_instance,
                token_type="Password reset"
            )

            self.validate_token_has_expired(token_instance, "Password reset")

            await self.user_repository.aupdate(
                db=db,
                instance=user,
                data={"hashed_password": pss.hash_password(data["password"])}
            )
            await self.prt_repository.adelete(
                db=db,
                instance=token_instance
            )
            await db.commit()
            return {"message": "Password is changed successfully"}
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while resetting password completion"
            )


class UserProfileService:

    def __init__(self) -> None:
        self.model_type = models.UserProfileModel
        self.profile_repository = repositories.UserProfileRepository()

    @staticmethod
    def validate_user_profile_not_found(
        current_user: models.UserModel
    ) -> None:
        if current_user.profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't have a profile"
            )

    async def get_current_user_profile(
        self,
        s3_service: S3Service,
        current_user: models.UserModel
    ) -> models.UserProfileModel:
        try:
            self.validate_user_profile_not_found(current_user)

            profile = current_user.profile
            profile.avatar = s3_service.get_image_url(profile.avatar)
            return profile
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting current user profile"
            )

    async def create_user_profile(
        self,
        db: AsyncSession,
        s3_service: S3Service,
        current_user: models.UserModel,
        data: dict
    ) -> models.UserProfileModel:
        try:
            profile = await self.profile_repository.aget_by(
                db=db,
                expressions=[self.model_type.user_id == current_user.id]
            )

            if profile:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already has a profile"
                )

            data["user_id"] = current_user.id
            avatar = data.pop("avatar", None)

            profile = await self.profile_repository.acreate(
                db=db,
                data=data
            )

            if avatar:
                profile.avatar = s3_service.upload_image(
                    identifier=profile.id,
                    image=avatar,
                    key_prefix="Avatars",
                    image_prefix="profile"
                )

            await db.commit()

            profile.avatar = (
                s3_service.get_image_url(profile.avatar)
                if avatar else None
            )
            return profile
        except (SQLAlchemyError, Boto3Error):
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating profile"
            )

    async def update_current_user_profile(
        self,
        db: AsyncSession,
        data: dict,
        current_user: models.UserModel,
        s3_service: S3Service
    ) -> models.UserProfileModel:
        try:
            self.validate_user_profile_not_found(current_user)

            profile = current_user.profile
            avatar = data.pop("avatar", None)

            await self.profile_repository.aupdate(
                db=db,
                instance=profile,
                data=data
            )
            await db.commit()

            if avatar:
                s3_service.delete_image(profile.avatar)
                s3_service.upload_image(
                    identifier=profile.id,
                    image=data["avatar"],
                    key_prefix="Avatars",
                    image_prefix="profile"
                )

            profile.avatar = s3_service.get_image_url(profile.avatar)
            return profile
        except (SQLAlchemyError, Boto3Error):
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating profile"
            )

    async def delete_current_user_profile(
        self,
        db: AsyncSession,
        s3_service: S3Service,
        current_user: models.UserModel
    ) -> None:
        try:
            self.validate_user_profile_not_found(current_user)

            await self.profile_repository.adelete(
                db=db,
                instance=current_user.profile
            )
            await db.commit()

            s3_service.delete_image(current_user.profile.avatar)
        except (SQLAlchemyError, Boto3Error):
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while profile deletion"
            )
