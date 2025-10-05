from __future__ import annotations

import csv
import csv
import zipfile
from pathlib import Path

from bank_normalizer.api import normalize_pdfs
from bank_normalizer.export import export_csv, export_xlsx
from bank_normalizer.export.lender_profiles import load_lender_profiles
from bank_normalizer.config import lenders as lenders_config

from .utils_pdf import build_bank_pdf


def test_csv_and_xlsx_exports(tmp_path: Path) -> None:
    pdf = build_bank_pdf("ANZ", tmp_path / "anz.pdf")
    bundle = normalize_pdfs([pdf])[0]
    csv_path = export_csv(bundle.transactions, tmp_path / "out.csv")
    xlsx_path = export_xlsx(bundle.transactions, tmp_path / "out.xlsx")
    assert csv_path.exists()
    assert xlsx_path.exists()
    with csv_path.open() as fh:
        reader = csv.reader(fh)
        header = next(reader)
        assert "amount" in [h.lower() for h in header]
    with zipfile.ZipFile(xlsx_path) as zf:
        sheet = zf.read("xl/worksheets/sheet1.xml")
        assert b"Transactions" in zf.read("xl/workbook.xml")
        assert b"WOOLWORTHS" in sheet


def test_lender_profile_transform(tmp_path: Path) -> None:
    pdf = build_bank_pdf("ANZ", tmp_path / "anz.pdf")
    bundle = normalize_pdfs([pdf])[0]
    profiles = load_lender_profiles(lenders_config.LENDERS)  # type: ignore[attr-defined]
    profile = profiles["lender_foo"]
    rows = [profile.transform(txn) for txn in bundle.transactions]
    profile.validate(rows)
    assert rows
