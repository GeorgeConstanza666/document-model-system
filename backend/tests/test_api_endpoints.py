"""
API integration tests.

These tests use a fresh in-memory SQLite DB for each test and mock
DocumentProcessor so KeyBERT / Google Translate are never called.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch

from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.models import Base
from app.schemas.document import DocTermDraft, ProcessedDocumentDraft, TechnologyDraft

TEST_DB_URL = "sqlite:///:memory:"

MOCK_PROCESSED = ProcessedDocumentDraft(
    file_name="report.txt",
    original_text="Python and FastAPI are used in this project. Python is great.",
    translated_text="Python and FastAPI are used in this project. Python is great.",
    source_language="en",
    extracted_terms=[
        DocTermDraft(term="fastapi", q_term=1, rel_freq_term=8.3333),
        DocTermDraft(term="python", q_term=2, rel_freq_term=16.6667),
    ],
    extracted_technologies=[
        TechnologyDraft(name="Python", degree_of_use=20.0),
        TechnologyDraft(name="FastAPI", degree_of_use=10.0),
    ],
)

FINALIZE_BODY = {
    "authors": [{"full_name": "Іван Коваленко", "contribution_percent": 100}],
    "domain_name": "Програмна інженерія",
}


@pytest.fixture()
def client():
    """TestClient backed by a fresh in-memory SQLite DB.

    StaticPool ensures all connections share the same in-memory DB so that
    tables created by create_all() are visible to every session.
    """
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def _upload(client: TestClient) -> str:
    """Mock-upload a file and return draft_id."""
    mock_proc = MagicMock()
    mock_proc.process.return_value = MOCK_PROCESSED
    with patch("app.api.routes.documents._get_processor", return_value=mock_proc):
        resp = client.post(
            "/api/documents/upload",
            files={"file": ("report.txt", b"Python and FastAPI...", "text/plain")},
        )
    assert resp.status_code == 200
    return resp.json()["draft_id"]


# ── Upload ─────────────────────────────────────────────────────────────────────

class TestUpload:
    def test_returns_draft_id_and_processed(self, client):
        draft_id = _upload(client)
        assert isinstance(draft_id, str) and len(draft_id) > 0

    def test_processed_contains_terms_and_technologies(self, client):
        mock_proc = MagicMock()
        mock_proc.process.return_value = MOCK_PROCESSED
        with patch("app.api.routes.documents._get_processor", return_value=mock_proc):
            resp = client.post(
                "/api/documents/upload",
                files={"file": ("report.txt", b"content", "text/plain")},
            )
        data = resp.json()["processed"]
        assert len(data["extracted_terms"]) == 2
        assert len(data["extracted_technologies"]) == 2

    def test_unsupported_format_returns_400(self, client):
        mock_proc = MagicMock()
        mock_proc.process.side_effect = ValueError("Unsupported extension: .xlsx")
        with patch("app.api.routes.documents._get_processor", return_value=mock_proc):
            resp = client.post(
                "/api/documents/upload",
                files={"file": ("data.xlsx", b"binary", "application/octet-stream")},
            )
        assert resp.status_code == 400


# ── Finalize ───────────────────────────────────────────────────────────────────

class TestFinalize:
    def test_creates_document_with_correct_data(self, client):
        draft_id = _upload(client)
        resp = client.post(f"/api/documents/{draft_id}/finalize", json=FINALIZE_BODY)
        assert resp.status_code == 201
        doc = resp.json()
        assert doc["subject_area"] == "Програмна інженерія"
        assert doc["authors"][0]["full_name"] == "Іван Коваленко"
        assert doc["authors"][0]["contribution_percent"] == 100.0
        assert len(doc["terms"]) == 2
        assert len(doc["technologies"]) == 2

    def test_creates_specialist_and_dictionary(self, client):
        draft_id = _upload(client)
        client.post(f"/api/documents/{draft_id}/finalize", json=FINALIZE_BODY)

        specialists = client.get("/api/specialists").json()
        assert len(specialists) == 1
        assert specialists[0]["document_count"] == 1
        assert specialists[0]["unique_term_count"] == 2

        dicts = client.get("/api/dictionaries").json()
        assert len(dicts) == 1
        assert dicts[0]["entry_count"] == 2

    def test_unknown_draft_id_returns_404(self, client):
        resp = client.post("/api/documents/no-such-id/finalize", json=FINALIZE_BODY)
        assert resp.status_code == 404

    def test_contributions_not_100_returns_422(self, client):
        draft_id = _upload(client)
        bad = {"authors": [{"full_name": "А", "contribution_percent": 60}],
               "domain_name": "Test"}
        resp = client.post(f"/api/documents/{draft_id}/finalize", json=bad)
        assert resp.status_code == 422

    def test_draft_removed_after_finalize(self, client):
        draft_id = _upload(client)
        client.post(f"/api/documents/{draft_id}/finalize", json=FINALIZE_BODY)
        resp = client.post(f"/api/documents/{draft_id}/finalize", json=FINALIZE_BODY)
        assert resp.status_code == 404


# ── Documents list / detail / delete ──────────────────────────────────────────

class TestDocumentsCRUD:
    def test_list_empty_initially(self, client):
        resp = client.get("/api/documents")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_list_shows_saved_document(self, client):
        draft_id = _upload(client)
        client.post(f"/api/documents/{draft_id}/finalize", json=FINALIZE_BODY)
        assert client.get("/api/documents").json()["total"] == 1

    def test_get_document_detail(self, client):
        draft_id = _upload(client)
        doc_id = client.post(
            f"/api/documents/{draft_id}/finalize", json=FINALIZE_BODY
        ).json()["id"]
        resp = client.get(f"/api/documents/{doc_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == doc_id

    def test_get_nonexistent_document_returns_404(self, client):
        assert client.get("/api/documents/9999").status_code == 404

    def test_delete_removes_document(self, client):
        draft_id = _upload(client)
        doc_id = client.post(
            f"/api/documents/{draft_id}/finalize", json=FINALIZE_BODY
        ).json()["id"]
        assert client.delete(f"/api/documents/{doc_id}").status_code == 204
        assert client.get("/api/documents").json()["total"] == 0


# ── Edge cases ─────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_finalize_empty_terms_uses_extracted_terms(self, client):
        """If body.terms is empty, finalize falls back to draft's extracted terms."""
        draft_id = _upload(client)
        body = {**FINALIZE_BODY, "terms": [], "technologies": []}
        resp = client.post(f"/api/documents/{draft_id}/finalize", json=body)
        assert resp.status_code == 201
        assert len(resp.json()["terms"]) == 2

    def test_upload_empty_content_returns_200(self, client):
        empty_draft = MOCK_PROCESSED.model_copy(
            update={"extracted_terms": [], "extracted_technologies": [],
                    "original_text": "", "translated_text": ""}
        )
        mock_proc = MagicMock()
        mock_proc.process.return_value = empty_draft
        with patch("app.api.routes.documents._get_processor", return_value=mock_proc):
            resp = client.post(
                "/api/documents/upload",
                files={"file": ("empty.txt", b"", "text/plain")},
            )
        assert resp.status_code == 200
        data = resp.json()["processed"]
        assert data["extracted_terms"] == []
        assert data["extracted_technologies"] == []

    def test_duplicate_domain_returns_409(self, client):
        client.post("/api/domains", json={"name": "Унікальний домен"})
        resp = client.post("/api/domains", json={"name": "Унікальний домен"})
        assert resp.status_code == 409
