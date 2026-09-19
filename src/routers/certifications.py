from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.pagination import PaginationDep
from src.dependencies.services import get_certification_service
from src.services.certifications import CertificationService
from src.schemas import certifications
from src.database.models.movies import CertificationModel


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
    response_model=certifications.CertificationDetailBaseSchema
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
