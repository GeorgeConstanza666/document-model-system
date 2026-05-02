from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.document import DocumentTechnology


class Technology(Base):
    """Technology referenced in one or more documents."""

    __tablename__ = "technologies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    document_technologies: Mapped[List["DocumentTechnology"]] = relationship(
        back_populates="technology"
    )
