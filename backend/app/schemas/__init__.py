from app.schemas.document import DocTermDraft, ProcessedDocumentDraft, TechnologyDraft
from app.schemas.requests import AuthorCreate, AuthorInput, DomainCreate, FinalizeDocumentRequest
from app.schemas.responses import (
    AuthorContribResponse,
    AuthorResponse,
    DocTechResponse,
    DocTermResponse,
    DocumentListItem,
    DocumentResponse,
    DomainResponse,
    PaginatedDocuments,
    UploadResponse,
)

__all__ = [
    "DocTermDraft",
    "TechnologyDraft",
    "ProcessedDocumentDraft",
    "AuthorInput",
    "FinalizeDocumentRequest",
    "DomainCreate",
    "AuthorCreate",
    "AuthorContribResponse",
    "DocTermResponse",
    "DocTechResponse",
    "DocumentResponse",
    "DocumentListItem",
    "PaginatedDocuments",
    "UploadResponse",
    "DomainResponse",
    "AuthorResponse",
]
