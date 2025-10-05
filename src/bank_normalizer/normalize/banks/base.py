from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ...extract.pdf_reader import PDFStatement


@dataclass
class SimpleBankProfile:
    name: str
    keywords: tuple[str, ...]
    mapping: Dict[str, str]

    def detect(self, statement: PDFStatement) -> float:
        text = statement.combined_text.upper()
        hits = sum(1 for keyword in self.keywords if keyword.upper() in text)
        return hits / max(len(self.keywords), 1)

    def column_map(self) -> Dict[str, str]:
        return self.mapping

    def clean_description(self, value: str) -> str:
        return " ".join(value.split())


__all__ = ["SimpleBankProfile"]
