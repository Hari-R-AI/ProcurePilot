"""Generic CRUD repository base class.

Provides common database operations for all repositories.
"""

from typing import Generic, TypeVar, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger(__name__)

# TypeVar for generic model
ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Generic CRUD repository for database access.
    
    Provides common operations:
    - Create
    - Read (by ID, all, by filter)
    - Update
    - Delete
    
    Type Parameters:
        ModelT: The ORM model class
        
    Example:
        >>> class UserRepository(BaseRepository[User]):
        ...     def __init__(self, db: AsyncSession):
        ...         super().__init__(User, db)
    """

    def __init__(self, model: type[ModelT], db: AsyncSession) -> None:
        """Initialize repository.
        
        Args:
            model: The ORM model class (e.g., ProcurementRequest)
            db: SQLAlchemy AsyncSession
        """
        self.model = model
        self.db = db

    async def create(self, obj_in: dict[str, Any]) -> ModelT:
        """Create a new record.
        
        Args:
            obj_in: Dictionary of attributes to set
            
        Returns:
            The created model instance
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        logger.debug(
            f"Created {self.model.__name__}",
            extra={"id": getattr(db_obj, "id", None)},
        )
        return db_obj

    async def get_by_id(self, id: int) -> Optional[ModelT]:
        """Get record by ID.
        
        Args:
            id: Primary key
            
        Returns:
            Model instance or None if not found
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[ModelT]:
        """Get all records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, id: int, obj_in: dict[str, Any]) -> Optional[ModelT]:
        """Update a record.
        
        Args:
            id: Primary key
            obj_in: Dictionary of attributes to update
            
        Returns:
            Updated model instance or None if not found
        """
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        logger.debug(
            f"Updated {self.model.__name__}",
            extra={"id": id},
        )
        return db_obj

    async def delete(self, id: int) -> bool:
        """Delete a record.
        
        Args:
            id: Primary key
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False
        
        await self.db.delete(db_obj)
        await self.db.commit()
        
        logger.debug(
            f"Deleted {self.model.__name__}",
            extra={"id": id},
        )
        return True

    async def count(self) -> int:
        """Count total records.
        
        Returns:
            Total number of records
        """
        result = await self.db.execute(
            select(self.model)
        )
        return len(result.scalars().all())
