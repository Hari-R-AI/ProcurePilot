"""Repository for Recommendation Log data access.

Provides database operations for audit trail and analysis history.
"""

from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import RecommendationLog
from app.db.repositories.base import BaseRepository

logger = get_logger(__name__)


class RecommendationLogRepository(BaseRepository[RecommendationLog]):
    """Repository for RecommendationLog data access.
    
    Provides:
    - Store analysis results
    - Retrieve analysis history
    - Query by request_id / trace_id
    - Search by confidence score
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.
        
        Args:
            db: SQLAlchemy AsyncSession
        """
        super().__init__(RecommendationLog, db)

    async def get_by_request_id(
        self,
        request_id: str,
    ) -> Optional[RecommendationLog]:
        """Get recommendation log by request ID.
        
        Args:
            request_id: Request tracking ID
            
        Returns:
            RecommendationLog or None if not found
        """
        result = await self.db.execute(
            select(RecommendationLog).where(
                RecommendationLog.request_id == request_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_trace_id(
        self,
        trace_id: str,
    ) -> Optional[RecommendationLog]:
        """Get recommendation log by trace ID.
        
        Args:
            trace_id: Distributed trace ID
            
        Returns:
            RecommendationLog or None if not found
        """
        result = await self.db.execute(
            select(RecommendationLog).where(
                RecommendationLog.trace_id == trace_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_procurement_request(
        self,
        procurement_request_id: int,
    ) -> list[RecommendationLog]:
        """Get recommendation logs for a procurement request.
        
        Args:
            procurement_request_id: Foreign key to ProcurementRequest
            
        Returns:
            List of RecommendationLog records
        """
        result = await self.db.execute(
            select(RecommendationLog)
            .where(
                RecommendationLog.procurement_request_id == procurement_request_id
            )
            .order_by(desc(RecommendationLog.created_at))
        )
        return result.scalars().all()

    async def get_latest_for_request(
        self,
        procurement_request_id: int,
    ) -> Optional[RecommendationLog]:
        """Get the latest recommendation log for a procurement request.

        Args:
            procurement_request_id: Foreign key to ProcurementRequest

        Returns:
            Latest RecommendationLog or None if not found
        """
        result = await self.db.execute(
            select(RecommendationLog)
            .where(
                RecommendationLog.procurement_request_id == procurement_request_id
            )
            .order_by(desc(RecommendationLog.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_high_confidence(
        self,
        min_score: float = 0.8,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RecommendationLog]:
        """Get recommendation logs with high confidence scores.
        
        Args:
            min_score: Minimum confidence score (0-1)
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of RecommendationLog records
        """
        result = await self.db.execute(
            select(RecommendationLog)
            .where(RecommendationLog.confidence_score >= min_score)
            .order_by(desc(RecommendationLog.confidence_score))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_low_confidence(
        self,
        max_score: float = 0.6,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RecommendationLog]:
        """Get recommendation logs with low confidence scores.
        
        Args:
            max_score: Maximum confidence score (0-1)
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of RecommendationLog records
        """
        result = await self.db.execute(
            select(RecommendationLog)
            .where(RecommendationLog.confidence_score <= max_score)
            .order_by(RecommendationLog.confidence_score)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_analyses(
        self,
        limit: int = 50,
    ) -> list[RecommendationLog]:
        """Get most recent analyses.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of most recent RecommendationLog records
        """
        result = await self.db.execute(
            select(RecommendationLog)
            .order_by(desc(RecommendationLog.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_stats(self) -> dict:
        """Get statistics about recommendations.
        
        Returns:
            Dictionary with:
            - total_analyses: Total number of analyses
            - avg_confidence: Average confidence score
            - high_confidence_count: Analyses with confidence >= 0.8
            - low_confidence_count: Analyses with confidence <= 0.6
        """
        from sqlalchemy import func
        
        # Get total count
        count_result = await self.db.execute(select(RecommendationLog))
        total = len(count_result.scalars().all())
        
        # Get average confidence
        avg_result = await self.db.execute(
            select(func.avg(RecommendationLog.confidence_score))
        )
        avg_confidence = avg_result.scalar() or 0.0
        
        # Get high confidence count
        high_result = await self.db.execute(
            select(func.count(RecommendationLog.id)).where(
                RecommendationLog.confidence_score >= 0.8
            )
        )
        high_count = high_result.scalar() or 0
        
        # Get low confidence count
        low_result = await self.db.execute(
            select(func.count(RecommendationLog.id)).where(
                RecommendationLog.confidence_score <= 0.6
            )
        )
        low_count = low_result.scalar() or 0
        
        return {
            "total_analyses": total,
            "avg_confidence": float(avg_confidence),
            "high_confidence_count": high_count,
            "low_confidence_count": low_count,
        }
