from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.document import AuthorContribution


class Author(Base):
    """Document author / project participant."""

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    contributions: Mapped[List["AuthorContribution"]] = relationship(back_populates="author")
    specialist: Mapped[Optional["Specialist"]] = relationship(
        back_populates="author", uselist=False
    )


class Specialist(Base):
    """Minimal specialist profile — links 1-to-1 to an Author."""

    __tablename__ = "specialists"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), unique=True)

    author: Mapped["Author"] = relationship(back_populates="specialist")
