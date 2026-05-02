from pathlib import Path

import pytest
from docx import Document as DocxDocument
from fpdf import FPDF

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEST_TEXT = "Hello from test fixture. Python is a programming language."


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Create fixture files once per test session and return their directory."""
    FIXTURES_DIR.mkdir(exist_ok=True)

    txt_path = FIXTURES_DIR / "sample.txt"
    txt_path.write_text(TEST_TEXT, encoding="utf-8")

    docx_path = FIXTURES_DIR / "sample.docx"
    doc = DocxDocument()
    doc.add_paragraph(TEST_TEXT)
    doc.save(str(docx_path))

    pdf_path = FIXTURES_DIR / "sample.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, TEST_TEXT)
    pdf.output(str(pdf_path))

    return FIXTURES_DIR
