import logging
import re

from deep_translator import GoogleTranslator
from langdetect import LangDetectException, detect

logger = logging.getLogger(__name__)

CHUNK_SIZE = 4500  # Google Translate hard limit is 5000; keep 500 chars of headroom


class TranslationService:
    """Detects language and translates text using Google Translate."""

    def detect_language(self, text: str) -> str:
        """Return the ISO 639-1 language code for *text* (e.g. 'en', 'uk').

        Returns 'unknown' when detection fails (text too short or ambiguous).
        """
        try:
            return detect(text)
        except LangDetectException as exc:
            logger.warning("Language detection failed: %s", exc)
            return "unknown"

    def translate(self, text: str, target_lang: str = "en") -> str:
        """Translate *text* to *target_lang*.

        Returns *text* unchanged when it is already in the target language or
        when the input is blank. Long texts are split at sentence boundaries
        so that each chunk stays within Google Translate's request limit.
        """
        if not text.strip():
            return text

        detected = self.detect_language(text)
        if detected == target_lang:
            return text

        chunks = self._split_into_chunks(text, CHUNK_SIZE)
        translated: list[str] = [self._translate_chunk(c, target_lang) for c in chunks]
        return " ".join(translated)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _translate_chunk(self, text: str, target: str) -> str:
        """Translate a single chunk via GoogleTranslator.

        Falls back to the original chunk on any error so the rest of the
        document is still returned.
        """
        try:
            result = GoogleTranslator(source="auto", target=target).translate(text)
            return result or text
        except Exception as exc:
            logger.error("Translation failed (chunk len=%d): %s", len(text), exc)
            return text

    @staticmethod
    def _split_into_chunks(text: str, max_size: int) -> list[str]:
        """Split *text* into pieces of at most *max_size* chars.

        Breaks are placed at sentence boundaries (after . ! ?) where possible.
        Sentences longer than *max_size* are split at the character level.
        """
        if len(text) <= max_size:
            return [text]

        sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s]

        chunks: list[str] = []
        current: list[str] = []

        for sentence in sentences:
            if len(sentence) > max_size:
                if current:
                    chunks.append(" ".join(current))
                    current = []
                for i in range(0, len(sentence), max_size):
                    chunks.append(sentence[i : i + max_size])
                continue

            candidate = " ".join(current + [sentence])
            if len(candidate) > max_size:
                chunks.append(" ".join(current))
                current = [sentence]
            else:
                current.append(sentence)

        if current:
            chunks.append(" ".join(current))

        return chunks
