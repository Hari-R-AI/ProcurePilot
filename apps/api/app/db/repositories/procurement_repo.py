"""Repository for Procurement Request data access.

Provides database operations specific to ProcurementRequest model.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import ProcurementRequest
from app.db.repositories.base import BaseRepository

logger = get_logger(__name__)


class ProcurementRepository(BaseRepository[ProcurementRequest]):
    """Repository for ProcurementRequest data access.
    
    Extends BaseRepository with domain-specific queries:
    - Get requests by category
    - Get requests by urgency
    - Get recent requests
    - Search requests
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.
        
        Args:
            db: SQLAlchemy AsyncSession
        """
        super().__init__(ProcurementRequest, db)

    async def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProcurementRequest]:
        """Get procurement requests by category.
        
        Args:
            category: Category to filter by (IT_HARDWARE, IT_SOFTWARE, etc.)
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of ProcurementRequest records
        """
        result = await self.db.execute(
            select(ProcurementRequest)
            .where(ProcurementRequest.category == category)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_urgency(
        self,
        urgency: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProcurementRequest]:
        """Get procurement requests by urgency level.
        
        Args:
            urgency: Urgency level (LOW, MEDIUM, HIGH, CRITICAL)
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of ProcurementRequest records
        """
        result = await self.db.execute(
            select(ProcurementRequest)
            .where(ProcurementRequest.urgency == urgency)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_department(
        self,
        department: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProcurementRequest]:
        """Get procurement requests by department.
        
        Args:
            department: Department name
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of ProcurementRequest records
        """
        result = await self.db.execute(
            select(ProcurementRequest)
            .where(ProcurementRequest.department == department)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent(self, limit: int = 20) -> list[ProcurementRequest]:
        """Get most recent procurement requests.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of most recent ProcurementRequest records
        """
        result = await self.db.execute(
            select(ProcurementRequest)
            .order_by(desc(ProcurementRequest.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def list_recent(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ProcurementRequest]:
        """List procurement requests ordered by newest first.

        Args:
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            List of ProcurementRequest records
        """
        result = await self.db.execute(
            select(ProcurementRequest)
            .order_by(desc(ProcurementRequest.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProcurementRequest]:
        """Search procurement requests by title or description.
        
        Args:
            query: Search query
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of matching ProcurementRequest records
        """
        search_pattern = f"%{query}%"
        result = await self.db.execute(
            select(ProcurementRequest)
            .where(
                (ProcurementRequest.title.ilike(search_pattern))
                | (ProcurementRequest.description.ilike(search_pattern))
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProcurementRequest]:
        """Get procurement requests within a date range.
        
        Args:
            start_date: Start datetime
            end_date: End datetime
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of ProcurementRequest records
        """
        result = await self.db.execute(
            select(ProcurementRequest)
            .where(
                (ProcurementRequest.created_at >= start_date)
                & (ProcurementRequest.created_at <= end_date)
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
