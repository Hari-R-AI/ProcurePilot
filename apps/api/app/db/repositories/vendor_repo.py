"""Vendor repository for database access."""

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Vendor
from app.api.v1.schemas.vendor import VendorCreate, VendorUpdate


class VendorRepository:
    """Repository for Vendor database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, vendor_in: VendorCreate) -> Vendor:
        """Create a new vendor."""
        db_vendor = Vendor(**vendor_in.model_dump())
        self.session.add(db_vendor)
        await self.session.commit()
        await self.session.refresh(db_vendor)
        return db_vendor

    async def get_by_id(self, vendor_id: int) -> Optional[Vendor]:
        """Get a vendor by ID."""
        result = await self.session.execute(
            select(Vendor).where(Vendor.id == vendor_id)
        )
        return result.scalar_one_or_none()

    async def get_by_gstin(self, gstin: str) -> Optional[Vendor]:
        """Get a vendor by GSTIN."""
        result = await self.session.execute(
            select(Vendor).where(Vendor.gstin == gstin)
        )
        return result.scalar_one_or_none()

    async def get_by_pan(self, pan_number: str) -> Optional[Vendor]:
        """Get a vendor by PAN."""
        result = await self.session.execute(
            select(Vendor).where(Vendor.pan_number == pan_number)
        )
        return result.scalar_one_or_none()

    async def list_vendors(self, skip: int = 0, limit: int = 50) -> List[Vendor]:
        """List all vendors."""
        result = await self.session.execute(
            select(Vendor).order_by(Vendor.legal_name.asc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count_vendors(self) -> int:
        """Count total vendors."""
        from sqlalchemy import func
        result = await self.session.execute(select(func.count()).select_from(Vendor))
        return result.scalar_one()

    async def update(self, vendor_id: int, vendor_in: VendorUpdate) -> Optional[Vendor]:
        """Update a vendor."""
        db_vendor = await self.get_by_id(vendor_id)
        if not db_vendor:
            return None

        update_data = vendor_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vendor, field, value)

        await self.session.commit()
        await self.session.refresh(db_vendor)
        return db_vendor

    async def delete(self, vendor_id: int) -> bool:
        """Delete a vendor."""
        db_vendor = await self.get_by_id(vendor_id)
        if not db_vendor:
            return False

        await self.session.delete(db_vendor)
        await self.session.commit()
        return True
