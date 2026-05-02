"""Tests for TermExtractor.

The KeyBERT model is loaded once per session to avoid repeated ~2 s startup.
"""
import pytest

from app.schemas.document import DocTermDraft
from app.services.nlp.term_extractor import TermExtractor

# A paragraph deliberately rich in repeated software-engineering terms so
# that KeyBERT has strong candidates and q_term > 0 is guaranteed.
_SE_TEXT = """
Software engineering is the systematic application of engineering principles
to the design, development, testing, and maintenance of software systems.
Software engineers apply software development methodologies such as Agile,
Scrum, and Kanban to manage software projects effectively.
The software development lifecycle includes requirements analysis, system
design, implementation, software testing, deployment, and software maintenance.
Code review is a critical practice in software engineering that improves
code quality and reduces defects in the software system.
Version control systems such as Git are fundamental tools in software
development, enabling teams to track code changes and collaborate on codebases.
Continuous integration and continuous deployment automate the software testing
and software deployment pipeline, allowing software teams to deliver
software updates faster and with higher quality assurance.
Software architecture defines the high-level structure of a software system
and the engineering decisions that shape its design and development.
""".strip()


@pytest.fixture(scope="module")
def extractor() -> TermExtractor:
    """Load KeyBERT once per test module (model init takes ~2 s)."""
    return TermExtractor()


# ---------------------------------------------------------------------------
# Structure tests
# ---------------------------------------------------------------------------


def test_returns_list_of_doc_term_drafts(extractor: TermExtractor) -> None:
    terms = extractor.extract(_SE_TEXT)
    assert isinstance(terms, list)
    assert len(terms) > 0
    assert all(isinstance(t, DocTermDraft) for t in terms)


def test_all_q_term_positive(extractor: TermExtractor) -> None:
    """Every returned term must actually appear in the source text."""
    terms = extractor.extract(_SE_TEXT)
    for t in terms:
        assert t.q_term > 0, f"q_term=0 for term '{t.term}'"


def test_sorted_by_rel_freq_descending(extractor: TermExtractor) -> None:
    terms = extractor.extract(_SE_TEXT)
    freqs = [t.rel_freq_term for t in terms]
    assert freqs == sorted(freqs, reverse=True)


def test_top_n_limits_result_count(extractor: TermExtractor) -> None:
    assert len(extractor.extract(_SE_TEXT, top_n=5)) <= 5
    assert len(extractor.extract(_SE_TEXT, top_n=10)) <= 10


def test_rel_freq_is_percentage_of_total_words(extractor: TermExtractor) -> None:
    terms = extractor.extract(_SE_TEXT)
    total_words = len(_SE_TEXT.split())
    for t in terms:
        expected = round(t.q_term / total_words * 100, 4)
        assert abs(t.rel_freq_term - expected) < 1e-3, (
            f"rel_freq_term mismatch for '{t.term}': "
            f"got {t.rel_freq_term}, expected {expected}"
        )


# ---------------------------------------------------------------------------
# Content / quality test
# ---------------------------------------------------------------------------


def test_software_engineering_terms_present(extractor: TermExtractor) -> None:
    """At least one term containing 'software' must appear in results."""
    terms = extractor.extract(_SE_TEXT)
    hits = [t for t in terms if "software" in t.term.lower()]
    assert hits, (
        f"No 'software'-related term found. Got: {[t.term for t in terms[:10]]}"
    )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_text_returns_empty_list(extractor: TermExtractor) -> None:
    assert extractor.extract("") == []
    assert extractor.extract("   ") == []
