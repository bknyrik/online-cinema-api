from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.pagination import PaginationDep
from src.dependencies.services import get_certification_service
from src.services.certifications import CertificationService
from src.schemas import certifications


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
