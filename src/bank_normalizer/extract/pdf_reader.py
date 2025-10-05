from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

@dataclass
class PDFPage:
    number: int
    text: str


@dataclass
class PDFStatement:
    path: Path
    pages: List[PDFPage]

    @property
    def combined_text(self) -> str:
        return "\n".join(page.text for page in self.pages)


def read_pdf(path: Path | str) -> PDFStatement:
    """Read a statement file and return text per page.

    The implementation favours plain-text inputs to keep the test environment
    lightweight. If :mod:`pdfplumber` is available it will be used, otherwise
    the file is treated as UTF-8 text.
    """

    pdf_path = Path(path)
    pages: List[PDFPage] = []
    try:  # pragma: no cover - optional dependency
        import pdfplumber  # type: ignore
    except Exception:
        text = pdf_path.read_text(encoding="utf-8")
        pages.append(PDFPage(number=1, text=text))
    else:  # pragma: no cover - dependency not available in tests
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.rotation and page.rotation % 360 != 0:
                    page = page.rotate(360 - page.rotation)
                text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                pages.append(PDFPage(number=page.page_number, text=text))
    return PDFStatement(path=pdf_path, pages=pages)


def iter_lines(statement: PDFStatement) -> Iterable[tuple[int, str]]:
    for page in statement.pages:
        for line in page.text.splitlines():
            cleaned = line.strip()
            if cleaned:
                yield page.number, cleaned


__all__ = ["read_pdf", "PDFStatement", "iter_lines"]
