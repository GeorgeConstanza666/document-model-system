"""
ORM model registry.

Import order matters: leaf models first, Document last (it imports all others).
Importing this package registers every model with Base.metadata.
"""
from app.models.base import Base
from app.models.term import Term
from app.models.technology import Technology
from app.models.author import Author, Specialist
from app.models.domain import Domain, Dictionary, DictionaryEntry
from app.models.document import Document, AuthorContribution, DocumentTerm, DocumentTechnology

__all__ = [
    "Base",
    "Term",
    "Technology",
    "Author",
    "Specialist",
    "Domain",
    "Dictionary",
    "DictionaryEntry",
    "Document",
    "AuthorContribution",
    "DocumentTerm",
    "DocumentTechnology",
]
