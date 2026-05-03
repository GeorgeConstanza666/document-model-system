"""Document endpoints: upload, finalize, list, retrieve, delete."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import AuthorContribution, Document, DocumentTechnology, DocumentTerm
from app.models.author import Author, Specialist
from app.models.domain import Dictionary, DictionaryEntry, Domain
from app.models.technology import Technology
from app.models.term import Term
from app.schemas.document import ProcessedDocumentDraft
from app.schemas.requests import FinalizeDocumentRequest
from app.schemas.responses import (
    AuthorContribResponse,
    DocTechResponse,
    DocTermResponse,
    DocumentListItem,
    DocumentResponse,
    PaginatedDocuments,
    UploadResponse,
)
from app.services.document_processor import DocumentProcessor

import tempfile
import os

router = APIRouter(prefix="/api/documents", tags=["documents"])

_drafts: dict[str, ProcessedDocumentDraft] = {}
_processor: Optional[DocumentProcessor] = None


def _get_processor() -> DocumentProcessor:
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor


def _build_doc_response(doc: Document) -> DocumentResponse:
    authors = [
        AuthorContribResponse(
            author_id=ac.author_id,
            full_name=ac.author.full_name,
            email=ac.author.email,
            contribution_percent=ac.contribution_percent,
        )
        for ac in doc.author_contributions
    ]
    terms = [
        DocTermResponse(
            term_id=dt.term_id,
            term=dt.term.text_en,
            q_term=dt.q_term,
            rel_freq_term=dt.rel_freq_term,
            definition=dt.term.definition,
        )
        for dt in doc.document_terms
    ]
    technologies = [
        DocTechResponse(
            technology_id=dtech.technology_id,
            technology_name=dtech.technology.name,
            degree_of_use=dtech.degree_of_use,
        )
        for dtech in doc.document_technologies
    ]
    return DocumentResponse(
        id=doc.id,
        file_name=doc.file_name,
        subject_area=doc.subject_area.name,
        date=doc.date,
        source_language=doc.source_language,
        original_text=doc.original_text,
        translated_text=doc.translated_text,
        authors=authors,
        terms=terms,
        technologies=technologies,
    )


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_200_OK)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """Parse and analyse an uploaded file; returns a draft for review before saving."""
    original_filename = file.filename or "document"
    suffix = os.path.splitext(original_filename)[1] or ".txt"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        processor = _get_processor()
        draft = processor.process(tmp_path)
        draft = draft.model_copy(update={"file_name": original_filename})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        os.unlink(tmp_path)

    draft_id = str(uuid.uuid4())
    _drafts[draft_id] = draft

    return UploadResponse(draft_id=draft_id, processed=draft)


@router.post(
    "/{draft_id}/finalize",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def finalize_document(
    draft_id: str,
    body: FinalizeDocumentRequest,
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """Persist a draft document together with authors, terms, and technologies."""
    draft = _drafts.get(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Чернетка не знайдена або вже збережена")

    # Get or create domain
    domain = db.query(Domain).filter(Domain.name == body.domain_name).first()
    if domain is None:
        domain = Domain(name=body.domain_name)
        db.add(domain)
        db.flush()

    doc = Document(
        subj_area_id=domain.id,
        date=body.date,
        original_text=draft.original_text,
        translated_text=draft.translated_text,
        source_language=draft.source_language,
        file_name=draft.file_name,
    )
    db.add(doc)
    db.flush()

    # Authors — track IDs for Specialist creation
    author_ids: list[int] = []
    for author_input in body.authors:
        author = db.query(Author).filter(Author.full_name == author_input.full_name).first()
        if author is None:
            author = Author(full_name=author_input.full_name, email=author_input.email)
            db.add(author)
            db.flush()
        author_ids.append(author.id)
        contrib = AuthorContribution(
            document_id=doc.id,
            author_id=author.id,
            contribution_percent=author_input.contribution_percent,
        )
        db.add(contrib)

    # Terms — track IDs for DictionaryEntry creation
    term_ids: list[int] = []
    terms_to_use = body.terms if body.terms else draft.extracted_terms
    for term_draft in terms_to_use:
        term = db.query(Term).filter(Term.text_en == term_draft.term).first()
        if term is None:
            term = Term(text_en=term_draft.term)
            db.add(term)
            db.flush()
        term_ids.append(term.id)
        doc_term = DocumentTerm(
            document_id=doc.id,
            term_id=term.id,
            q_term=term_draft.q_term,
            rel_freq_term=term_draft.rel_freq_term,
        )
        db.add(doc_term)

    # Technologies
    techs_to_use = body.technologies if body.technologies else draft.extracted_technologies
    for tech_draft in techs_to_use:
        tech = db.query(Technology).filter(Technology.name == tech_draft.name).first()
        if tech is None:
            tech = Technology(name=tech_draft.name)
            db.add(tech)
            db.flush()
        doc_tech = DocumentTechnology(
            document_id=doc.id,
            technology_id=tech.id,
            degree_of_use=tech_draft.degree_of_use,
        )
        db.add(doc_tech)

    # Specialists — get-or-create for each author
    for author_id in author_ids:
        if not db.query(Specialist).filter(Specialist.author_id == author_id).first():
            db.add(Specialist(author_id=author_id))

    # Dictionary — get-or-create for this domain
    dictionary = db.query(Dictionary).filter(Dictionary.domain_id == domain.id).first()
    if dictionary is None:
        dictionary = Dictionary(domain_id=domain.id)
        db.add(dictionary)
        db.flush()

    # DictionaryEntries — link each term to the dictionary if not already linked
    for term_id in term_ids:
        exists = db.query(DictionaryEntry).filter(
            DictionaryEntry.dictionary_id == dictionary.id,
            DictionaryEntry.term_id == term_id,
        ).first()
        if exists is None:
            db.add(DictionaryEntry(dictionary_id=dictionary.id, term_id=term_id))

    db.commit()
    db.refresh(doc)
    del _drafts[draft_id]

    return _build_doc_response(doc)


@router.get("", response_model=PaginatedDocuments)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> PaginatedDocuments:
    """Return a paginated list of all documents."""
    total = db.query(Document).count()
    docs = (
        db.query(Document)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [
        DocumentListItem(
            id=doc.id,
            file_name=doc.file_name,
            subject_area=doc.subject_area.name,
            date=doc.date,
            source_language=doc.source_language,
            authors=[ac.author.full_name for ac in doc.author_contributions],
            term_count=len(doc.document_terms),
            technology_count=len(doc.document_technologies),
        )
        for doc in docs
    ]
    return PaginatedDocuments(items=items, total=total, page=page, page_size=page_size)


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db)) -> DocumentResponse:
    """Return full details for a single document."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="Документ не знайдено")
    return _build_doc_response(doc)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(doc_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a document and all its related rows."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="Документ не знайдено")

    db.query(AuthorContribution).filter(AuthorContribution.document_id == doc_id).delete()
    db.query(DocumentTerm).filter(DocumentTerm.document_id == doc_id).delete()
    db.query(DocumentTechnology).filter(DocumentTechnology.document_id == doc_id).delete()
    db.delete(doc)
    db.commit()
