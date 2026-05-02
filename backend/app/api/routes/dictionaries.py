"""Dictionary (vocabulary) endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.domain import Dictionary
from app.schemas.responses import DictionaryDetail, DictionaryListItem, DictionaryTermEntry

router = APIRouter(prefix="/api/dictionaries", tags=["dictionaries"])


@router.get("", response_model=list[DictionaryListItem])
def list_dictionaries(db: Session = Depends(get_db)) -> list[DictionaryListItem]:
    """Return all dictionaries with their entry counts."""
    dictionaries = db.query(Dictionary).all()
    return [
        DictionaryListItem(
            id=d.id,
            domain_name=d.domain.name,
            entry_count=len(d.entries),
        )
        for d in dictionaries
    ]


@router.get("/{dictionary_id}", response_model=DictionaryDetail)
def get_dictionary(dictionary_id: int, db: Session = Depends(get_db)) -> DictionaryDetail:
    """Return dictionary details with terms and their document occurrence counts."""
    d = db.query(Dictionary).filter(Dictionary.id == dictionary_id).first()
    if d is None:
        raise HTTPException(status_code=404, detail="Словник не знайдено")

    entries = [
        DictionaryTermEntry(
            term_id=entry.term.id,
            term=entry.term.text_en,
            document_count=len(entry.term.document_terms),
        )
        for entry in d.entries
    ]
    entries.sort(key=lambda e: e.document_count, reverse=True)

    return DictionaryDetail(id=d.id, domain_name=d.domain.name, entries=entries)
