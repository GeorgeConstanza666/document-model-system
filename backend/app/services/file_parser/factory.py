from pathlib import Path

from app.services.file_parser.base import FileParser
from app.services.file_parser.docx_parser import DocxParser
from app.services.file_parser.pdf_parser import PdfParser
from app.services.file_parser.txt_parser import TxtParser

_PARSERS: dict[str, type[FileParser]] = {
    ".docx": DocxParser,
    ".pdf": PdfParser,
    ".txt": TxtParser,
}


def get_parser(file_path: str) -> FileParser:
    """Return the appropriate FileParser for *file_path* based on its extension.

    Raises:
        ValueError: if the file extension is not supported.
    """
    ext = Path(file_path).suffix.lower()
    parser_class = _PARSERS.get(ext)
    if parser_class is None:
        supported = ", ".join(_PARSERS)
        raise ValueError(f"Unsupported file type '{ext}'. Supported: {supported}")
    return parser_class()
