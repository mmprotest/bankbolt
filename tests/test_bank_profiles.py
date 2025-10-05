from __future__ import annotations

from pathlib import Path

from bank_normalizer.api import normalize_pdfs

from .utils_pdf import build_bank_pdf


BANKS = ["ANZ", "CBA", "NAB", "Westpac"]


def test_bank_detection(tmp_path: Path) -> None:
    for bank in BANKS:
        pdf = build_bank_pdf(bank, tmp_path / f"{bank}.pdf")
        bundle = normalize_pdfs([pdf])[0]
        assert bank in bundle.meta.bank
        assert bundle.meta.pages >= 1
