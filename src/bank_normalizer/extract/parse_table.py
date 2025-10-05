from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from .pdf_reader import PDFStatement, iter_lines

DATE_RE = re.compile(r"\b(\d{1,2}[/-][A-Za-z]{3}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")
AMOUNT_RE = re.compile(r"[-+]?\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|[-+]?\d+\.\d{2}|\(\$?\d+(?:,\d{3})*(?:\.\d{2})?\)")


@dataclass
class ParsedRow:
    page: int
    raw: Dict[str, str]


HEADER_TOKENS = {"date", "description", "debit", "withdrawal", "credit", "deposit", "amount", "balance"}


def _split_columns(line: str) -> List[str]:
    parts = [part.strip() for part in re.split(r"\s{2,}", line) if part.strip()]
    return parts


def find_header(lines: Iterable[str]) -> Optional[int]:
    for idx, line in enumerate(lines):
        lowered = {token.strip().lower() for token in re.split(r"\s+", line)}
        if HEADER_TOKENS & lowered:
            return idx
    return None


def parse_statement_rows(statement: PDFStatement) -> List[ParsedRow]:
    rows: List[ParsedRow] = []
    page_lines: Dict[int, List[str]] = {}
    for page_num, line in iter_lines(statement):
        page_lines.setdefault(page_num, []).append(line)

    for page_num, lines in page_lines.items():
        header_idx = find_header(lines)
        if header_idx is None:
            continue
        header_tokens = _split_columns(lines[header_idx])
        for line in lines[header_idx + 1 :]:
            if not DATE_RE.search(line) and not any(token.lower() in line.lower() for token in ("balance", "total")):
                if rows:
                    rows[-1].raw["Description"] = f"{rows[-1].raw.get('Description', '')} {line.strip()}".strip()
                continue
            columns = _split_columns(line)
            if len(columns) < 2:
                continue
            raw_map: Dict[str, str] = {}
            for idx, token in enumerate(header_tokens):
                if idx < len(columns):
                    raw_map[token] = columns[idx]
            rows.append(ParsedRow(page=page_num, raw=raw_map))
    return rows


def parse_date(value: str) -> Optional[datetime]:
    try:
        from dateparser import parse as parse_dateparser
    except ImportError:  # pragma: no cover - optional dependency
        return None
    dt = parse_dateparser(value, settings={"DATE_ORDER": "DMY", "PREFER_DAY_OF_MONTH": "first"})
    return dt


__all__ = ["ParsedRow", "parse_statement_rows", "parse_date"]
