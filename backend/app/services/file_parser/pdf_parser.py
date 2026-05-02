import pdfplumber

from app.services.file_parser.base import FileParser


class PdfParser(FileParser):
    """Extracts text from .pdf files using pdfplumber (all pages joined)."""

    def extract_text(self, file_path: str) -> str:
        pages: list[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n".join(pages)
