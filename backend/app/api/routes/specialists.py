"""Specialist endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.author import Specialist
from app.schemas.responses import SpecialistDetail, SpecialistDocument, SpecialistListItem

router = APIRouter(prefix="/api/specialists", tags=["specialists"])


@router.get("", response_model=list[SpecialistListItem])
def list_specialists(db: Session = Depends(get_db)) -> list[SpecialistListItem]:
    """Return all specialists with their document and unique-term counts."""
    specialists = db.query(Specialist).all()
    result = []
    for spec in specialists:
        author = spec.author
        unique_term_ids: set[int] = set()
        for contrib in author.contributions:
            for dt in contrib.document.document_terms:
                unique_term_ids.add(dt.term_id)
        result.append(
            SpecialistListItem(
                id=spec.id,
                author_id=author.id,
                full_name=author.full_name,
                email=author.email,
                document_count=len(author.contributions),
                unique_term_count=len(unique_term_ids),
            )
        )
    return result


@router.get("/{specialist_id}", response_model=SpecialistDetail)
def get_specialist(specialist_id: int, db: Session = Depends(get_db)) -> SpecialistDetail:
    """Return full details for a specialist: documents and unique terms."""
    spec = db.query(Specialist).filter(Specialist.id == specialist_id).first()
    if spec is None:
        raise HTTPException(status_code=404, detail="Спеціаліст не знайдений")

    author = spec.author
    docs: list[SpecialistDocument] = []
    unique_terms: dict[int, str] = {}
    unique_technologies: dict[int, str] = {}

    for contrib in author.contributions:
        doc = contrib.document
        docs.append(
            SpecialistDocument(
                id=doc.id,
                file_name=doc.file_name,
                date=doc.date,
                subject_area=doc.subject_area.name,
            )
        )
        for dt in doc.document_terms:
            unique_terms[dt.term_id] = dt.term.text_en
        for dtech in doc.document_technologies:
            unique_technologies[dtech.technology_id] = dtech.technology.name

    return SpecialistDetail(
        id=spec.id,
        author_id=author.id,
        full_name=author.full_name,
        email=author.email,
        documents=docs,
        unique_terms=sorted(unique_terms.values()),
        unique_technologies=sorted(unique_technologies.values()),
    )


@router.delete("/{specialist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_specialist(specialist_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a specialist record (the linked author and documents are kept)."""
    spec = db.query(Specialist).filter(Specialist.id == specialist_id).first()
    if spec is None:
        raise HTTPException(status_code=404, detail="Спеціаліст не знайдений")
    db.delete(spec)
    db.commit()
