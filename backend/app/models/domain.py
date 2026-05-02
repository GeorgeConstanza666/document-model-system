from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.term import Term

if TYPE_CHECKING:
    from app.models.document import Document


class Domain(Base):
    """Subject area / domain — maps to SubjArea in the document model."""

    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    documents: Mapped[List["Document"]] = relationship(back_populates="subject_area")
    dictionaries: Mapped[List["Dictionary"]] = relationship(back_populates="domain")


class Dictionary(Base):
    """Vocabulary dictionary for a domain (minimal Vocab module)."""

    __tablename__ = "dictionaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))

    domain: Mapped["Domain"] = relationship(back_populates="dictionaries")
    entries: Mapped[List["DictionaryEntry"]] = relationship(back_populates="dictionary")


class DictionaryEntry(Base):
    """Links a Term to a Dictionary (minimal Vocab module)."""

    __tablename__ = "dictionary_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    dictionary_id: Mapped[int] = mapped_column(ForeignKey("dictionaries.id"))
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id"))

    dictionary: Mapped["Dictionary"] = relationship(back_populates="entries")
    term: Mapped["Term"] = relationship(back_populates="dictionary_entries")
