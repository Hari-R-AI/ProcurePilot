"""SQLAlchemy declarative base and configuration.

Provides the declarative base for all ORM models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models.
    
    All SQLAlchemy models should inherit from this class.
    
    Example:
        >>> class MyModel(Base):
        ...     __tablename__ = "my_model"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
    """

    pass
