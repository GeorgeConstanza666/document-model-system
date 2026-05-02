from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.schemas.document import ProcessedDocumentDraft


class AuthorContribResponse(BaseModel):
    author_id: int
    full_name: str
    email: Optional[str] = None
    contribution_percent: float


class DocTermResponse(BaseModel):
    term_id: int
    term: str
    q_term: int
    rel_freq_term: float


class DocTechResponse(BaseModel):
    technology_id: int
    technology_name: str
    degree_of_use: float


class DocumentResponse(BaseModel):
    id: int
    file_name: Optional[str] = None
    subject_area: str
    date: date
    source_language: Optional[str] = None
    original_text: Optional[str] = None
    translated_text: Optional[str] = None
    authors: list[AuthorContribResponse]
    terms: list[DocTermResponse]
    technologies: list[DocTechResponse]


class DocumentListItem(BaseModel):
    id: int
    file_name: Optional[str] = None
    subject_area: str
    date: date
    source_language: Optional[str] = None
    authors: list[str]
    term_count: int
    technology_count: int


class PaginatedDocuments(BaseModel):
    items: list[DocumentListItem]
    total: int
    page: int
    page_size: int


class UploadResponse(BaseModel):
    draft_id: str
    processed: ProcessedDocumentDraft


class DomainResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class AuthorResponse(BaseModel):
    id: int
    full_name: str
    email: Optional[str] = None
