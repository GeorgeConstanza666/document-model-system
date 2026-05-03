import logging
from pathlib import Path


from app.schemas.document import ProcessedDocumentDraft
from app.services.file_parser.factory import get_parser
from app.services.nlp.technology_extractor import TechnologyExtractor
from app.services.nlp.term_extractor import TermExtractor
from app.services.translation.translator import TranslationService

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Orchestrates the full document processing pipeline.

    Steps performed by :meth:`process`:
    1. Parse file text via the file-parser factory.
    2. Detect source language.
    3. Translate to English when the source is not English.
    4. Extract key terms from the English text (KeyBERT + frequency).
    5. Extract technology mentions from the English text.
    6. Return a :class:`~app.schemas.document.ProcessedDocumentDraft`.

    Nothing is persisted to the database at this stage.
    """

    def __init__(self) -> None:
        self.translator = TranslationService()
        self.term_extractor = TermExtractor()
        self.tech_extractor = TechnologyExtractor()

    def process(self, file_path: str) -> ProcessedDocumentDraft:
        """Run the full pipeline for the file at *file_path*."""
        file_name = Path(file_path).name
        logger.info("Processing '%s'", file_name)

        # Step 1 — parse
        parser = get_parser(file_path)
        original_text = parser.extract_text(file_path)
        logger.info("Parsed %d chars from '%s'", len(original_text), file_name)

        # Step 2 — detect language
        source_language = self.translator.detect_language(original_text)
        logger.info("Detected language: '%s' (text length: %d chars)", source_language, len(original_text))

        # Step 3 — translate if needed
        if source_language == "en":
            logger.info("Text already in English — skipping translation")
            translated_text = original_text
        else:
            logger.info("Translating %d chars '%s' → English …", len(original_text), source_language)
            translated_text = self.translator.translate(original_text, target_lang="en")
            ukr_in_trans = sum(1 for c in translated_text if 1024 <= ord(c) <= 1279)
            logger.info(
                "Translation done. Result: %d chars, %.1f%% Cyrillic chars",
                len(translated_text),
                100 * ukr_in_trans / len(translated_text) if translated_text else 0,
            )

        # Step 4 — extract terms
        extracted_terms = self.term_extractor.extract(translated_text)
        logger.info("Extracted %d terms", len(extracted_terms))

        # Step 5 — extract technologies
        extracted_technologies = self.tech_extractor.extract(translated_text)
        logger.info("Detected %d technologies", len(extracted_technologies))

        return ProcessedDocumentDraft(
            file_name=file_name,
            original_text=original_text,
            translated_text=translated_text,
            source_language=source_language,
            extracted_terms=extracted_terms,
            extracted_technologies=extracted_technologies,
        )
