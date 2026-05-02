import json
import re
from pathlib import Path

from app.schemas.document import TechnologyDraft

_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "technologies.json"

# These names are short / ambiguous enough to require exact case matching.
_CASE_SENSITIVE: frozenset[str] = frozenset({"Go", "R", "C", "C#", "C++", "F#", "pip"})


def _build_pattern(name: str) -> re.Pattern[str]:
    """Compile a word-boundary regex for *name*, respecting case rules."""
    escaped = re.escape(name)
    # Use word boundary only where the edge char is alphanumeric / underscore.
    prefix = r"\b" if name[0].isalnum() or name[0] == "_" else r"(?<![a-zA-Z0-9_])"
    suffix = r"\b" if name[-1].isalnum() or name[-1] == "_" else r"(?![a-zA-Z0-9_])"
    flags = 0 if name in _CASE_SENSITIVE else re.IGNORECASE
    return re.compile(prefix + escaped + suffix, flags)


class TechnologyExtractor:
    """Detects technology mentions in English text using a curated keyword list."""

    def __init__(self) -> None:
        names: list[str] = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
        # Pre-compile every pattern once at construction time.
        self._patterns: list[tuple[str, re.Pattern[str]]] = [
            (name, _build_pattern(name)) for name in names
        ]

    def extract(self, text_en: str) -> list[TechnologyDraft]:
        """Return technologies found in *text_en*, sorted by degree_of_use descending.

        degree_of_use = min(100, mention_count × 10).
        Only technologies with at least one mention are included.
        """
        results: list[TechnologyDraft] = []
        for name, pattern in self._patterns:
            count = len(pattern.findall(text_en))
            if count >= 1:
                results.append(
                    TechnologyDraft(
                        name=name,
                        degree_of_use=min(100.0, count * 10.0),
                    )
                )
        results.sort(key=lambda t: -t.degree_of_use)
        return results
