from app.services.file_parser.base import FileParser

_ENCODINGS = ("utf-8", "cp1251", "latin-1")


class TxtParser(FileParser):
    """Extracts text from .txt files, probing common encodings in order."""

    def extract_text(self, file_path: str) -> str:
        for enc in _ENCODINGS:
            try:
                with open(file_path, encoding=enc) as fh:
                    return fh.read()
            except UnicodeDecodeError:
                continue
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
