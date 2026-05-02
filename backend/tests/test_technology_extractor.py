"""Tests for TechnologyExtractor."""
import pytest

from app.schemas.document import TechnologyDraft
from app.services.nlp.technology_extractor import TechnologyExtractor

_MAIN_TEXT = (
    "This project uses FastAPI as the web framework and Python as the programming "
    "language. The data is stored in a PostgreSQL database, and Redis is used for "
    "caching. The application is containerised with Docker and deployed to AWS using "
    "GitHub Actions for continuous integration. Python scripts handle the ETL pipeline "
    "with Pandas and NumPy. FastAPI endpoints are covered by pytest tests."
)

_AMBIGUOUS_TEXT = (
    "We chose Go for the backend microservices because Go offers excellent concurrency. "
    "The team also evaluated R for data analysis but ultimately went with Python instead."
)


@pytest.fixture(scope="module")
def extractor() -> TechnologyExtractor:
    return TechnologyExtractor()


# ---------------------------------------------------------------------------
# Core requirements
# ---------------------------------------------------------------------------


def test_detects_fastapi_python_postgresql(extractor: TechnologyExtractor) -> None:
    results = extractor.extract(_MAIN_TEXT)
    names = {t.name for t in results}
    assert "FastAPI" in names, f"FastAPI not found; got {names}"
    assert "Python" in names, f"Python not found; got {names}"
    assert "PostgreSQL" in names, f"PostgreSQL not found; got {names}"


def test_returns_only_present_technologies(extractor: TechnologyExtractor) -> None:
    """No technology with zero mentions may appear in the results."""
    results = extractor.extract(_MAIN_TEXT)
    assert all(t.degree_of_use >= 10 for t in results), (
        "degree_of_use must be ≥ 10 (i.e. at least 1 mention)"
    )


def test_degree_of_use_formula(extractor: TechnologyExtractor) -> None:
    """2 mentions → degree 20; ≥10 mentions → capped at 100."""
    # FastAPI appears exactly twice in _MAIN_TEXT
    results = extractor.extract(_MAIN_TEXT)
    fastapi = next(t for t in results if t.name == "FastAPI")
    assert fastapi.degree_of_use == 20.0

    python = next(t for t in results if t.name == "Python")
    assert python.degree_of_use == 20.0  # 2 mentions


def test_degree_of_use_capped_at_100(extractor: TechnologyExtractor) -> None:
    dense_text = ("Python " * 15).strip()  # 15 mentions → would be 150 without cap
    results = extractor.extract(dense_text)
    python_entry = next(t for t in results if t.name == "Python")
    assert python_entry.degree_of_use == 100.0


def test_sorted_by_degree_of_use_descending(extractor: TechnologyExtractor) -> None:
    results = extractor.extract(_MAIN_TEXT)
    degrees = [t.degree_of_use for t in results]
    assert degrees == sorted(degrees, reverse=True)


def test_returns_list_of_technology_drafts(extractor: TechnologyExtractor) -> None:
    results = extractor.extract(_MAIN_TEXT)
    assert isinstance(results, list)
    assert all(isinstance(t, TechnologyDraft) for t in results)


# ---------------------------------------------------------------------------
# Case-sensitivity tests
# ---------------------------------------------------------------------------


def test_go_is_case_sensitive(extractor: TechnologyExtractor) -> None:
    """'Go' must not match 'go' in common English words like 'going'."""
    text = "We are going to use a good approach for golang projects."
    results = extractor.extract(text)
    names = {t.name for t in results}
    assert "Go" not in names, "'Go' should not match lowercase 'go' / 'going' / 'golang'"


def test_go_matches_when_capitalised(extractor: TechnologyExtractor) -> None:
    results = extractor.extract("The backend is written in Go and deployed on AWS.")
    names = {t.name for t in results}
    assert "Go" in names


def test_r_is_case_sensitive(extractor: TechnologyExtractor) -> None:
    """'R' must not match the letter 'r' mid-word."""
    text = "Rust is great for performance-critical parts of the system."
    results = extractor.extract(text)
    names = {t.name for t in results}
    assert "R" not in names


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_text_returns_empty_list(extractor: TechnologyExtractor) -> None:
    assert extractor.extract("") == []


def test_no_technologies_in_text(extractor: TechnologyExtractor) -> None:
    results = extractor.extract("The weather is sunny and warm today.")
    assert results == []
