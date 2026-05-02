from pathlib import Path

import pytest

from app.services.file_parser.docx_parser import DocxParser
from app.services.file_parser.factory import get_parser
from app.services.file_parser.pdf_parser import PdfParser
from app.services.file_parser.txt_parser import TxtParser

EXPECTED = "Hello from test fixture"


def test_txt_parser(fixtures_dir: Path) -> None:
    path = str(fixtures_dir / "sample.txt")
    assert EXPECTED in TxtParser().extract_text(path)


def test_docx_parser(fixtures_dir: Path) -> None:
    path = str(fixtures_dir / "sample.docx")
    assert EXPECTED in DocxParser().extract_text(path)


def test_pdf_parser(fixtures_dir: Path) -> None:
    path = str(fixtures_dir / "sample.pdf")
    assert EXPECTED in PdfParser().extract_text(path)


def test_factory_returns_correct_parser_types(fixtures_dir: Path) -> None:
    assert isinstance(get_parser(str(fixtures_dir / "sample.txt")), TxtParser)
    assert isinstance(get_parser(str(fixtures_dir / "sample.docx")), DocxParser)
    assert isinstance(get_parser(str(fixtures_dir / "sample.pdf")), PdfParser)


def test_factory_raises_for_unsupported_extension() -> None:
    with pytest.raises(ValueError, match="Unsupported file type '.xlsx'"):
        get_parser("report.xlsx")
