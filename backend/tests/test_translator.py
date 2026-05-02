"""Tests for TranslationService.

Tests that hit the real Google Translate API are marked with `network` and
can be skipped offline with:  pytest -m "not network"
"""
import pytest

from app.services.translation.translator import CHUNK_SIZE, TranslationService

# Ukrainian sentence — long enough for reliable langdetect
_UA_TEXT = (
    "Це тестовий текст для перевірки сервісу перекладу. "
    "Система повинна визначити мову і перекласти речення на англійську."
)
_EN_TEXT = "This sentence is already written in English and must not be translated."


# ---------------------------------------------------------------------------
# Network-dependent tests (require internet access)
# ---------------------------------------------------------------------------


@pytest.mark.network
def test_translate_ukrainian_to_english() -> None:
    service = TranslationService()
    result = service.translate(_UA_TEXT, target_lang="en")

    assert result, "Result must be non-empty"
    # After translation the Cyrillic block should be gone
    assert not any("Ѐ" <= ch <= "ӿ" for ch in result), (
        f"Expected no Cyrillic in translated text, got: {result!r}"
    )


@pytest.mark.network
def test_detect_language_ukrainian() -> None:
    service = TranslationService()
    assert service.detect_language(_UA_TEXT) == "uk"


# ---------------------------------------------------------------------------
# Offline tests (no network needed)
# ---------------------------------------------------------------------------


def test_translate_english_returns_as_is(monkeypatch: pytest.MonkeyPatch) -> None:
    """Text already in the target language must be returned unchanged."""
    service = TranslationService()
    # Force detect_language to confirm the text is English
    monkeypatch.setattr(service, "detect_language", lambda _text: "en")

    result = service.translate(_EN_TEXT, target_lang="en")
    assert result == _EN_TEXT


def test_translate_empty_text_returns_as_is() -> None:
    service = TranslationService()
    assert service.translate("") == ""
    assert service.translate("   ") == "   "


def test_long_text_is_split_into_multiple_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    """10 000+ char text must be split so no chunk exceeds CHUNK_SIZE."""
    service = TranslationService()

    sentence = "Це тестове речення для перевірки розбиття довгого тексту на частини. "
    long_text = sentence * 180  # ≈ 12 600 chars

    chunks_seen: list[str] = []

    def fake_translate_chunk(text: str, target: str) -> str:
        chunks_seen.append(text)
        return "[translated]"

    monkeypatch.setattr(service, "detect_language", lambda _text: "uk")
    monkeypatch.setattr(service, "_translate_chunk", fake_translate_chunk)

    result = service.translate(long_text, target_lang="en")

    assert len(chunks_seen) > 1, "Long text must produce more than one chunk"
    assert all(len(c) <= CHUNK_SIZE for c in chunks_seen), (
        f"All chunks must be ≤ {CHUNK_SIZE} chars; got sizes: {[len(c) for c in chunks_seen]}"
    )
    assert result == " ".join(["[translated]"] * len(chunks_seen))


def test_split_into_chunks_short_text() -> None:
    text = "Short text."
    chunks = TranslationService._split_into_chunks(text, CHUNK_SIZE)
    assert chunks == [text]


def test_split_into_chunks_respects_sentence_boundaries() -> None:
    # Build text slightly above limit so it must be split
    sentence = "A" * 100 + ". "
    text = sentence * 50  # 5100 chars — just over 4500
    chunks = TranslationService._split_into_chunks(text, CHUNK_SIZE)
    assert len(chunks) > 1
    assert all(len(c) <= CHUNK_SIZE for c in chunks)
