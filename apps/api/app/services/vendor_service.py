"""Vendor business logic and compliance validation."""

from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse, VendorListResponse
from app.core.exceptions import ValidationException
from app.db.repositories.vendor_repo import VendorRepository


class VendorService:
    """Service handling vendor onboarding and validation."""

    def __init__(self, db_session: AsyncSession):
        self.repo = VendorRepository(db_session)

    async def create_vendor(self, vendor_in: VendorCreate) -> VendorResponse:
        """Create a new vendor with compliance validation.
        
        Validates uniqueness of GSTIN and PAN.
        Performs realistic compliance placeholder checks.
        """
        # 1. Validation
        await self._validate_uniqueness(vendor_in.gstin, vendor_in.pan_number, vendor_in.cin_number, vendor_in.udyam_number)
        
        # 2. Check GST-PAN relationship
        if not vendor_in.gstin[2:12] == vendor_in.pan_number:
            raise ValidationException(
                detail="GSTIN characters 3-12 must match the PAN exactly.",
                code="INVALID_GSTIN_PAN_RELATION"
            )

        # 3. Create Vendor (starts as PENDING or VERIFIED based on mock check)
        # Note: In a real ERP system, this would call GSTN API.
        db_vendor = await self.repo.create(vendor_in)

        # Mock External API Validation (Indian Compliance Readiness)
        # If MSME is checked but Udyam is missing, we could flag it.
        compliance_status = "VERIFIED"
        if vendor_in.msme_registered and not vendor_in.udyam_number:
            compliance_status = "PENDING"
            
        if db_vendor.compliance_status != compliance_status:
            db_vendor = await self.repo.update(db_vendor.id, VendorUpdate(compliance_status=compliance_status))

        return VendorResponse.model_validate(db_vendor)

    async def get_vendor(self, vendor_id: int) -> Optional[VendorResponse]:
        """Get vendor by ID."""
        vendor = await self.repo.get_by_id(vendor_id)
        if not vendor:
            return None
        return VendorResponse.model_validate(vendor)

    async def list_vendors(self, skip: int = 0, limit: int = 50) -> VendorListResponse:
        """Get a list of vendors."""
        vendors = await self.repo.list_vendors(skip, limit)
        total = await self.repo.count_vendors()
        return VendorListResponse(
            vendors=[VendorResponse.model_validate(v) for v in vendors],
            total=total
        )

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------
    
    async def _validate_uniqueness(self, gstin: str, pan: str, cin: Optional[str] = None, udyam: Optional[str] = None) -> None:
        """Validate that the vendor identifiers are unique in the database."""
        if await self.repo.get_by_gstin(gstin):
            raise ValidationException(detail=f"Vendor with GSTIN {gstin} already exists.", code="DUPLICATE_GSTIN")
        if await self.repo.get_by_pan(pan):
            raise ValidationException(detail=f"Vendor with PAN {pan} already exists.", code="DUPLICATE_PAN")
        
        # Note: In production we would add unique checks for CIN and Udyam as well.
