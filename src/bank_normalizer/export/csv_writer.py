from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from ..models import Transaction

DEFAULT_COLUMNS = [
    "date",
    "description",
    "merchant",
    "category",
    "amount",
    "debit",
    "credit",
    "balance",
    "bank",
    "account",
]


def export_csv(transactions: Iterable[Transaction], path: Path) -> Path:
    rows = [
        [
            txn.date.strftime("%Y-%m-%d"),
            txn.description,
            txn.merchant or "",
            txn.category or "",
            f"{txn.amount:.2f}",
            f"{txn.debit:.2f}" if txn.debit is not None else "",
            f"{txn.credit:.2f}" if txn.credit is not None else "",
            f"{txn.balance:.2f}" if txn.balance is not None else "",
            txn.bank,
            txn.account or "",
        ]
        for txn in transactions
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(DEFAULT_COLUMNS)
        writer.writerows(rows)
    return path


__all__ = ["export_csv", "DEFAULT_COLUMNS"]
