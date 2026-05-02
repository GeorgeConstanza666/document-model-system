from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.document import DocumentTerm
    from app.models.domain import DictionaryEntry


class Term(Base):
    """NLP-extracted term, normalised to English."""

    __tablename__ = "terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    text_en: Mapped[str] = mapped_column(String(255), unique=True)
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    document_terms: Mapped[List["DocumentTerm"]] = relationship(back_populates="term")
    dictionary_entries: Mapped[List["DictionaryEntry"]] = relationship(back_populates="term")
