from docx import Document

from app.services.file_parser.base import FileParser


class DocxParser(FileParser):
    """Extracts text from .docx files using python-docx."""

    def extract_text(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
