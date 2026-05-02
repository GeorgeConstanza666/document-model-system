from datetime import date as date_type
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.document import DocTermDraft, TechnologyDraft


class AuthorInput(BaseModel):
    """Single author with their contribution share."""

    full_name: str = Field(min_length=1)
    email: Optional[str] = None
    contribution_percent: float = Field(gt=0, le=100)


class FinalizeDocumentRequest(BaseModel):
    """Body for POST /api/documents/{draft_id}/finalize."""

    authors: list[AuthorInput] = Field(min_length=1)
    domain_name: str = Field(min_length=1)
    date: date_type = Field(default_factory=date_type.today)
    terms: list[DocTermDraft] = Field(default_factory=list)
    technologies: list[TechnologyDraft] = Field(default_factory=list)

    @model_validator(mode="after")
    def _contributions_must_sum_to_100(self) -> "FinalizeDocumentRequest":
        total = sum(a.contribution_percent for a in self.authors)
        if abs(total - 100.0) > 0.01:
            raise ValueError(
                f"Author contributions must sum to 100 %, got {total:.2f} %"
            )
        return self


class DomainCreate(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None


class AuthorCreate(BaseModel):
    full_name: str = Field(min_length=1)
    email: Optional[str] = None
