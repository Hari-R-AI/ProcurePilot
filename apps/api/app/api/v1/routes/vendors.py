"""Vendor onboarding API routes.

Provides endpoints for vendor management:
- POST /vendors
- GET /vendors
- GET /vendors/{id}
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.vendor import VendorCreate, VendorResponse, VendorListResponse
from app.core.exceptions import ValidationException
from app.core.logging import get_logger
from app.db.session import get_db_session
from app.services.vendor_service import VendorService

logger = get_logger(__name__)

router = APIRouter()


def get_vendor_service(db: AsyncSession = Depends(get_db_session)) -> VendorService:
    """Dependency: provide a VendorService instance."""
    return VendorService(db)


ServiceDep = Annotated[VendorService, Depends(get_vendor_service)]


@router.post(
    "",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Onboard Vendor",
    description="Register a new vendor and run preliminary Indian compliance validation.",
    tags=["vendors"],
)
async def onboard_vendor(
    vendor_in: VendorCreate,
    service: ServiceDep,
) -> VendorResponse:
    """Onboard a new vendor."""
    logger.info("Onboarding new vendor", extra={"gstin": vendor_in.gstin})
    try:
        return await service.create_vendor(vendor_in)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail,
        )


@router.get(
    "",
    response_model=VendorListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Vendors",
    tags=["vendors"],
)
async def list_vendors(
    service: ServiceDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> VendorListResponse:
    """List registered vendors."""
    return await service.list_vendors(skip=skip, limit=limit)


@router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Vendor",
    tags=["vendors"],
)
async def get_vendor(
    vendor_id: int,
    service: ServiceDep,
) -> VendorResponse:
    """Get a specific vendor profile."""
    vendor = await service.get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor #{vendor_id} not found"
        )
    return vendor
