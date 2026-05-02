"""Author endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.author import Author
from app.schemas.requests import AuthorCreate
from app.schemas.responses import AuthorResponse

router = APIRouter(prefix="/api/authors", tags=["authors"])


@router.get("", response_model=list[AuthorResponse])
def list_authors(
    search: str = Query("", description="Filter by name substring"),
    db: Session = Depends(get_db),
) -> list[AuthorResponse]:
    """Return all authors, optionally filtered by name."""
    query = db.query(Author)
    if search:
        query = query.filter(Author.full_name.ilike(f"%{search}%"))
    authors = query.order_by(Author.full_name).all()
    return [AuthorResponse(id=a.id, full_name=a.full_name, email=a.email) for a in authors]


@router.post("", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(body: AuthorCreate, db: Session = Depends(get_db)) -> AuthorResponse:
    """Create a new author."""
    existing = db.query(Author).filter(Author.full_name == body.full_name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Автор з таким іменем вже існує")
    author = Author(full_name=body.full_name, email=body.email)
    db.add(author)
    db.commit()
    db.refresh(author)
    return AuthorResponse(id=author.id, full_name=author.full_name, email=author.email)
