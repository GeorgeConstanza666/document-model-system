from datetime import date
from typing import List, Optional

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.author import Author
from app.models.base import Base
from app.models.domain import Domain
from app.models.technology import Technology
from app.models.term import Term


class Document(Base):
    """
    Core document entity.

    Implements formula 3 from the paper:
    Doc = ⟨idD, sAuthor, SubjArea, Date, sDocTerm, sTechnology⟩
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    subj_area_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    date: Mapped[date] = mapped_column(Date)
    original_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    translated_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    subject_area: Mapped["Domain"] = relationship(back_populates="documents")
    author_contributions: Mapped[List["AuthorContribution"]] = relationship(
        back_populates="document"
    )
    document_terms: Mapped[List["DocumentTerm"]] = relationship(back_populates="document")
    document_technologies: Mapped[List["DocumentTechnology"]] = relationship(
        back_populates="document"
    )


class AuthorContribution(Base):
    """
    Author contribution to a document — sAuthor element.

    Invariant: sum of contribution_percent per document_id == 100.
    """

    __tablename__ = "author_contributions"
    __table_args__ = (UniqueConstraint("document_id", "author_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    contribution_percent: Mapped[float] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="author_contributions")
    author: Mapped["Author"] = relationship(back_populates="contributions")


class DocumentTerm(Base):
    """
    Term occurrence inside a document — DocTerm = ⟨Term, qTerm, relFreqTerm⟩.
    """

    __tablename__ = "document_terms"
    __table_args__ = (UniqueConstraint("document_id", "term_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id"))
    q_term: Mapped[int] = mapped_column(Integer)
    rel_freq_term: Mapped[float] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="document_terms")
    term: Mapped["Term"] = relationship(back_populates="document_terms")


class DocumentTechnology(Base):
    """
    Technology usage in a document — Technology = ⟨nameTech, degreeOfUseTech⟩.
    """

    __tablename__ = "document_technologies"
    __table_args__ = (UniqueConstraint("document_id", "technology_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    technology_id: Mapped[int] = mapped_column(ForeignKey("technologies.id"))
    degree_of_use: Mapped[float] = mapped_column(Float)

    document: Mapped["Document"] = relationship(back_populates="document_technologies")
    technology: Mapped["Technology"] = relationship(back_populates="document_technologies")
