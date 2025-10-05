from __future__ import annotations

from pathlib import Path
from typing import Iterable

try:  # pragma: no cover - optional dependency
    import pytesseract
    from pdf2image import convert_from_path  # type: ignore
except Exception:  # pragma: no cover
    pytesseract = None
    convert_from_path = None


def ocr_pdf(path: Path | str) -> Iterable[str]:  # pragma: no cover - optional
    if pytesseract is None or convert_from_path is None:
        raise RuntimeError("OCR dependencies not installed")
    images = convert_from_path(str(path))
    for image in images:
        yield pytesseract.image_to_string(image)
