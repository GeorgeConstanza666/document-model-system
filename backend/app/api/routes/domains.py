"""Domain (subject area) endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.domain import Domain
from app.schemas.requests import DomainCreate
from app.schemas.responses import DomainResponse

router = APIRouter(prefix="/api/domains", tags=["domains"])


@router.get("", response_model=list[DomainResponse])
def list_domains(db: Session = Depends(get_db)) -> list[DomainResponse]:
    """Return all domains."""
    domains = db.query(Domain).order_by(Domain.name).all()
    return [DomainResponse(id=d.id, name=d.name, description=d.description) for d in domains]


@router.post("", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
def create_domain(body: DomainCreate, db: Session = Depends(get_db)) -> DomainResponse:
    """Create a new domain. Returns 409 if name already exists."""
    existing = db.query(Domain).filter(Domain.name == body.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Домен з такою назвою вже існує")
    domain = Domain(name=body.name, description=body.description)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return DomainResponse(id=domain.id, name=domain.name, description=domain.description)
