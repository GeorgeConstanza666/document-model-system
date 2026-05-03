"""Term endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.term import Term

router = APIRouter(prefix="/api/terms", tags=["terms"])


class TermDefinitionUpdate(BaseModel):
    definition: Optional[str] = None


@router.patch("/{term_id}", response_model=dict)
def update_term_definition(
    term_id: int,
    body: TermDefinitionUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update the definition of a term (TermDefinition from formula 2)."""
    term = db.query(Term).filter(Term.id == term_id).first()
    if term is None:
        raise HTTPException(status_code=404, detail="Термін не знайдено")
    term.definition = body.definition
    db.commit()
    db.refresh(term)
    return {"id": term.id, "text_en": term.text_en, "definition": term.definition}
