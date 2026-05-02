import logging
import re

from keybert import KeyBERT

from app.schemas.document import DocTermDraft

logger = logging.getLogger(__name__)


class TermExtractor:
    """Extracts key terms from English text using KeyBERT + frequency analysis."""

    def __init__(self) -> None:
        logger.info("Loading KeyBERT model 'all-MiniLM-L6-v2' …")
        self._model = KeyBERT(model="all-MiniLM-L6-v2")

    def extract(self, text_en: str, top_n: int = 30) -> list[DocTermDraft]:
        """Return the top *top_n* terms from *text_en* ranked by relative frequency.

        Steps:
        1. Generate keyword candidates with KeyBERT (1–3 word n-grams).
        2. For each candidate count whole-word occurrences (case-insensitive).
        3. Compute rel_freq_term = q_term / total_words * 100.
        4. Sort by rel_freq_term descending; return top_n.
        """
        if not text_en.strip():
            return []

        words = text_en.split()
        total_words = len(words)
        if total_words == 0:
            return []

        # Ask KeyBERT for extra candidates so filtering doesn't cut the list short.
        candidates = self._model.extract_keywords(
            text_en,
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            top_n=top_n + 20,
        )

        results: list[DocTermDraft] = []
        for keyword, _score in candidates:
            pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
            q_term = len(pattern.findall(text_en))
            if q_term == 0:
                continue
            rel_freq = round(q_term / total_words * 100, 4)
            results.append(DocTermDraft(term=keyword, q_term=q_term, rel_freq_term=rel_freq))

        results.sort(key=lambda d: (-d.rel_freq_term, d.term))
        return results[:top_n]
