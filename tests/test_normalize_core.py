from __future__ import annotations

from pathlib import Path

from bank_normalizer.api import normalize_pdfs
from bank_normalizer.models import ResultBundle

from .utils_pdf import build_bank_pdf


def test_normalization_basic(tmp_path: Path) -> None:
    pdf = build_bank_pdf("ANZ", tmp_path / "anz.pdf")
    bundles = normalize_pdfs([pdf])
    assert len(bundles) == 1
    bundle = bundles[0]
    assert bundle.meta.bank == "ANZ"
    assert len(bundle.transactions) > 5
    debits = [txn.debit for txn in bundle.transactions if txn.debit]
    assert all(debit > 0 for debit in debits)
    amounts = [txn.amount for txn in bundle.transactions]
    assert any(amount < 0 for amount in amounts)
    assert any(txn.category == "GROCERIES" for txn in bundle.transactions)
