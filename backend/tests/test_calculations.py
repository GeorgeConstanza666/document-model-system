"""
Unit tests for the document-model mathematical formulas.

These tests verify the paper's formulas directly without loading NLP models:
  - q_term:       count of term occurrences in text (whole-word, case-insensitive)
  - rel_freq_term: round(q_term / total_words * 100, 4)
  - degree_of_use: min(100.0, mention_count * 10.0)
"""

import re


def _count_occurrences(text: str, keyword: str) -> int:
    pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
    return len(pattern.findall(text))


def _rel_freq_term(q_term: int, total_words: int) -> float:
    return round(q_term / total_words * 100, 4)


def _degree_of_use(mention_count: int) -> float:
    return min(100.0, mention_count * 10.0)


# ── q_term ────────────────────────────────────────────────────────────────────

class TestQTerm:
    def test_single_occurrence(self):
        assert _count_occurrences("python is a language", "python") == 1

    def test_multiple_occurrences(self):
        assert _count_occurrences("python python python java", "python") == 3

    def test_case_insensitive(self):
        assert _count_occurrences("Python PYTHON python", "python") == 3

    def test_whole_word_boundary(self):
        # "pythonista" must not count as "python"
        assert _count_occurrences("pythonista and python", "python") == 1

    def test_multiword_term(self):
        text = "machine learning is part of machine learning research"
        assert _count_occurrences(text, "machine learning") == 2

    def test_zero_occurrences(self):
        assert _count_occurrences("java is a language", "python") == 0

    def test_empty_text(self):
        assert _count_occurrences("", "python") == 0


# ── rel_freq_term ─────────────────────────────────────────────────────────────

class TestRelFreqTerm:
    def test_two_in_hundred(self):
        assert _rel_freq_term(2, 100) == 2.0

    def test_rounds_to_4_decimals(self):
        # 1/3 * 100 = 33.3333...
        assert _rel_freq_term(1, 3) == round(100 / 3, 4)

    def test_zero_count(self):
        assert _rel_freq_term(0, 50) == 0.0

    def test_all_words_are_term(self):
        # every word is the term
        assert _rel_freq_term(5, 5) == 100.0

    def test_proportional_to_q_term(self):
        r1 = _rel_freq_term(1, 20)
        r2 = _rel_freq_term(2, 20)
        assert r2 == pytest.approx(r1 * 2)


import pytest


# ── degree_of_use ─────────────────────────────────────────────────────────────

class TestDegreeOfUse:
    def test_single_mention(self):
        assert _degree_of_use(1) == 10.0

    def test_three_mentions(self):
        assert _degree_of_use(3) == 30.0

    def test_capped_at_100(self):
        assert _degree_of_use(15) == 100.0

    def test_exactly_10_hits_cap(self):
        assert _degree_of_use(10) == 100.0

    def test_nine_not_capped(self):
        assert _degree_of_use(9) == 90.0

    def test_zero_mentions(self):
        assert _degree_of_use(0) == 0.0
