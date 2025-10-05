from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ...models import Transaction


@dataclass
class BarLenderProfile:
    name: str = "Bar Lend Loans"

    def columns(self) -> List[str]:
        return [
            "Date",
            "Debit",
            "Credit",
            "Category",
        ]

    def transform(self, txn: Transaction) -> Dict[str, object]:
        return {
            "Date": txn.date.strftime("%Y-%m-%d"),
            "Debit": round(abs(txn.amount), 2) if txn.amount < 0 else 0.0,
            "Credit": round(txn.amount, 2) if txn.amount > 0 else 0.0,
            "Category": txn.category or "UNCATEGORISED",
        }

    def validate(self, rows: List[Dict[str, object]]) -> None:
        for row in rows:
            if row["Debit"] < 0 or row["Credit"] < 0:
                raise ValueError("Negative values not allowed")


PROFILE = BarLenderProfile()
