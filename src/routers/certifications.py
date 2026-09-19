from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.authentication import get_current_moderator_or_admin
from src.dependencies.pagination import PaginationDep
from src.dependencies.services import get_certification_service
from src.services.certifications import CertificationService
from src.schemas import certifications
from src.database.models.movies import CertificationModel
from src.database.models.accounts import UserModel


router = APIRouter()


@router.get(
    "/",
    response_model=certifications.CertificationListResponseSchema
)
async def get_certification_list(
    pagination_data: PaginationDep,
    db: AsyncSession = Depends(get_db),
    certification_service: CertificationService = Depends(get_certification_service),
) -> dict:
    return await certification_service.get_certification_list(
        pagination_data=pagination_data,
        db=db
    )


@router.get(
    "/{certification_id}/",
    response_model=certifications.CertificationDetailResponseSchema
)
async def get_certification_detail(
    certification_id: int,
    db: AsyncSession = Depends(get_db),
    certification_service: CertificationService = Depends(get_certification_service)
) -> CertificationModel:
    return await certification_service.get_certification_detail(
        db=db,
        certification_id=certification_id
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=certifications.CertificationDetailResponseSchema
)
async def create_certification(
    data: certifications.CertificationCreateRequestSchema,
    db: AsyncSession = Depends(get_db),
    certification_service: CertificationService = Depends(get_certification_service),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> CertificationModel:
    return await certification_service.create_certification(
        db=db,
        data=data.model_dump()
    )


@router.put(
    "/{certification_id}/",
    response_model=certifications.CertificationDetailResponseSchema
)
async def update_certification(
    certification_id: int,
    data: certifications.CertificationDataRequestSchema,
    db: AsyncSession = Depends(get_db),
    certification_service: CertificationService = Depends(get_certification_service),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> CertificationModel:
    return await certification_service.update_certification(
        db=db,
        certification_id=certification_id,
        data=data.model_dump()
    )


@router.delete(
    "/{certification_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_certification(
    certification_id: int,
    db: AsyncSession = Depends(get_db),
    certification_service: CertificationService = Depends(get_certification_service),
    current_user: UserModel = Depends(get_current_moderator_or_admin)
) -> None:
    return await certification_service.delete_certification(
        db=db,
        certification_id=certification_id
    )
