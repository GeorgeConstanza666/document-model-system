"""Integration tests for DocumentProcessor.

Network tests call Google Translate — skip offline with:
    pytest tests/test_document_processor.py -m "not network" -v
"""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.schemas.document import ProcessedDocumentDraft
from app.services.document_processor import DocumentProcessor


@pytest.fixture(scope="module")
def processor() -> DocumentProcessor:
    """One DocumentProcessor instance shared across all module tests."""
    return DocumentProcessor()


# ---------------------------------------------------------------------------
# Integration tests (network + KeyBERT)
# ---------------------------------------------------------------------------


@pytest.mark.network
def test_process_returns_processed_document_draft(
    processor: DocumentProcessor,
    ua_it_docx_path: Path,
) -> None:
    result = processor.process(str(ua_it_docx_path))
    assert isinstance(result, ProcessedDocumentDraft)


@pytest.mark.network
def test_process_detects_ukrainian_language(
    processor: DocumentProcessor,
    ua_it_docx_path: Path,
) -> None:
    result = processor.process(str(ua_it_docx_path))
    assert result.source_language == "uk", (
        f"Expected source_language='uk', got '{result.source_language}'"
    )


@pytest.mark.network
def test_process_translates_to_english(
    processor: DocumentProcessor,
    ua_it_docx_path: Path,
) -> None:
    result = processor.process(str(ua_it_docx_path))
    assert result.translated_text, "translated_text must not be empty"
    cyrillic = [ch for ch in result.translated_text if "Ѐ" <= ch <= "ӿ"]
    assert not cyrillic, (
        f"Translated text still contains Cyrillic: {''.join(cyrillic[:20])!r}"
    )


@pytest.mark.network
def test_process_original_text_preserved(
    processor: DocumentProcessor,
    ua_it_docx_path: Path,
) -> None:
    result = processor.process(str(ua_it_docx_path))
    # Original must contain Ukrainian text
    assert any("Ѐ" <= ch <= "ӿ" or "Ѐ" <= ch <= "ӿ" for ch in result.original_text), (
        "original_text should contain Ukrainian (Cyrillic) characters"
    )


@pytest.mark.network
def test_process_extracts_expected_technologies(
    processor: DocumentProcessor,
    ua_it_docx_path: Path,
) -> None:
    result = processor.process(str(ua_it_docx_path))
    tech_names = {t.name for t in result.extracted_technologies}
    # These appear verbatim in the UA text and survive Google Translate unchanged
    must_find = {"Python", "FastAPI", "PostgreSQL", "Docker"}
    missing = must_find - tech_names
    assert not missing, (
        f"Expected technologies not found: {missing}. "
        f"Got: {sorted(tech_names)}"
    )


@pytest.mark.network
def test_process_extracts_terms_with_positive_q_term(
    processor: DocumentProcessor,
    ua_it_docx_path: Path,
) -> None:
    result = processor.process(str(ua_it_docx_path))
    assert len(result.extracted_terms) > 0, "No terms extracted"
    bad = [t for t in result.extracted_terms if t.q_term == 0]
    assert not bad, f"Terms with q_term=0: {[t.term for t in bad]}"


@pytest.mark.network
def test_process_file_name_equals_basename(
    processor: DocumentProcessor,
    ua_it_docx_path: Path,
) -> None:
    result = processor.process(str(ua_it_docx_path))
    assert result.file_name == ua_it_docx_path.name


# ---------------------------------------------------------------------------
# Offline unit test — tests orchestration logic without network or KeyBERT
# ---------------------------------------------------------------------------


def test_english_document_skips_translation(fixtures_dir: Path) -> None:
    """When source language is English, translate() must never be called."""
    # Use __new__ to bypass __init__ (avoids loading KeyBERT / TranslationService).
    proc = DocumentProcessor.__new__(DocumentProcessor)
    proc.translator = MagicMock()
    proc.translator.detect_language.return_value = "en"
    proc.term_extractor = MagicMock()
    proc.term_extractor.extract.return_value = []
    proc.tech_extractor = MagicMock()
    proc.tech_extractor.extract.return_value = []

    result = proc.process(str(fixtures_dir / "sample.docx"))

    proc.translator.translate.assert_not_called()
    assert result.source_language == "en"
    assert result.translated_text == result.original_text
    assert result.file_name == "sample.docx"
    assert isinstance(result, ProcessedDocumentDraft)
