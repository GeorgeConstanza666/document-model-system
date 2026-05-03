"""Dictionary (vocabulary) endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.domain import Dictionary, DictionaryEntry
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
            definition=entry.term.definition,
        )
        for entry in d.entries
    ]
    entries.sort(key=lambda e: e.document_count, reverse=True)

    return DictionaryDetail(id=d.id, domain_name=d.domain.name, entries=entries)


@router.delete("/{dictionary_id}/terms/{term_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_term_from_dictionary(
    dictionary_id: int, term_id: int, db: Session = Depends(get_db)
) -> None:
    """Remove a term entry from a dictionary (the Term record itself is kept)."""
    entry = db.query(DictionaryEntry).filter(
        DictionaryEntry.dictionary_id == dictionary_id,
        DictionaryEntry.term_id == term_id,
    ).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    db.delete(entry)
    db.commit()


@router.delete("/{dictionary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dictionary(dictionary_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a dictionary and all its entries."""
    d = db.query(Dictionary).filter(Dictionary.id == dictionary_id).first()
    if d is None:
        raise HTTPException(status_code=404, detail="Словник не знайдено")
    db.query(DictionaryEntry).filter(DictionaryEntry.dictionary_id == dictionary_id).delete()
    db.delete(d)
    db.commit()
