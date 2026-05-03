import logging
import re
import time

from langdetect import LangDetectException, detect

logger = logging.getLogger(__name__)

# Chunk size for Google Translate fallback (unofficial API limit: 5000 chars)
_GOOGLE_CHUNK_SIZE = 4500
_RETRY_ATTEMPTS = 3
_RETRY_DELAY = 1.0


class TranslationService:
    """Detects language and translates text.

    Primary engine: argostranslate (offline, no rate limits).
    Fallback: Google Translate unofficial API (chunked, with retry).
    """

    def __init__(self) -> None:
        self._argos_ready = self._init_argos()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_language(self, text: str) -> str:
        """Return the ISO 639-1 language code for *text* (e.g. 'en', 'uk').

        Uses a sample of the text to avoid langdetect misclassifying large
        documents that contain many English technical terms as English.
        """
        sample = text[:2000] if len(text) <= 2000 else text[500:2500]
        try:
            result = detect(sample)
            logger.info("Language detected: %s (sample %d chars)", result, len(sample))
            return result
        except LangDetectException:
            try:
                result = detect(text[:500])
                logger.info("Language detected (fallback): %s", result)
                return result
            except LangDetectException as exc:
                logger.warning("Language detection failed: %s", exc)
                return "unknown"

    def translate(self, text: str, target_lang: str = "en") -> str:
        """Translate *text* to *target_lang*.

        Tries argostranslate first (offline), falls back to Google Translate.
        Returns *text* unchanged when it is already in the target language or
        when the input is blank.
        """
        if not text.strip():
            return text

        detected = self.detect_language(text)
        if detected == target_lang:
            return text

        if self._argos_ready:
            result = self._translate_argos(text, detected, target_lang)
            if result is not None:
                return result

        logger.warning("argostranslate unavailable — falling back to Google Translate")
        return self._translate_google(text, target_lang)

    # ------------------------------------------------------------------
    # argostranslate (offline)
    # ------------------------------------------------------------------

    def _init_argos(self) -> bool:
        """Return True if uk->en argostranslate model is installed."""
        try:
            from argostranslate.translate import get_translation_from_codes
            t = get_translation_from_codes("uk", "en")
            if t is not None:
                logger.info("argostranslate uk->en model ready (offline translation)")
                return True
            logger.warning(
                "argostranslate uk->en model not installed. "
                "Run: python scripts/download_models.py"
            )
        except ImportError:
            logger.warning("argostranslate not installed")
        except Exception as exc:
            logger.warning("argostranslate init check failed: %s", exc)
        return False

    def _translate_argos(self, text: str, source_code: str, target_code: str) -> str | None:
        """Translate using argostranslate offline. Returns None on failure."""
        try:
            from argostranslate.translate import get_translation_from_codes
            t = get_translation_from_codes(source_code, target_code)
            if t is None:
                logger.warning(
                    "argostranslate: no %s->%s model installed", source_code, target_code
                )
                return None
            translated = t.translate(text)
            logger.info("argostranslate: translated %d chars offline", len(text))
            return translated
        except Exception as exc:
            logger.error("argostranslate translation error: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Google Translate fallback (unofficial API, chunked)
    # ------------------------------------------------------------------

    def _translate_google(self, text: str, target_lang: str) -> str:
        from deep_translator import GoogleTranslator  # noqa: PLC0415

        chunks = self._split_into_chunks(text, _GOOGLE_CHUNK_SIZE)
        translated: list[str] = []
        for i, chunk in enumerate(chunks):
            translated.append(self._google_chunk(chunk, target_lang))
            if i < len(chunks) - 1:
                time.sleep(0.3)
        return " ".join(translated)

    def _google_chunk(self, text: str, target: str) -> str:
        from deep_translator import GoogleTranslator  # noqa: PLC0415

        last_exc: Exception | None = None
        for attempt in range(1, _RETRY_ATTEMPTS + 1):
            try:
                result = GoogleTranslator(source="auto", target=target).translate(text)
                return result or text
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "Google Translate attempt %d/%d failed (chunk len=%d): %s",
                    attempt, _RETRY_ATTEMPTS, len(text), exc,
                )
                if attempt < _RETRY_ATTEMPTS:
                    time.sleep(_RETRY_DELAY)
        logger.error("All %d Google Translate attempts failed: %s", _RETRY_ATTEMPTS, last_exc)
        return text

    @staticmethod
    def _split_into_chunks(text: str, max_size: int) -> list[str]:
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
                    chunks.append(sentence[i: i + max_size])
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
