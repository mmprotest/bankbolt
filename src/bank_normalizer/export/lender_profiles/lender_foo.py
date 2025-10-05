from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ...models import Transaction


@dataclass
class FooLenderProfile:
    name: str = "Foo Bank Mortgage"

    def columns(self) -> List[str]:
        return [
            "Transaction Date",
            "Description",
            "Amount",
            "Balance",
        ]

    def transform(self, txn: Transaction) -> Dict[str, object]:
        return {
            "Transaction Date": txn.date.strftime("%d/%m/%Y"),
            "Description": txn.description,
            "Amount": round(txn.amount, 2),
            "Balance": round(txn.balance or 0.0, 2) if txn.balance is not None else "",
        }

    def validate(self, rows: List[Dict[str, object]]) -> None:
        for row in rows:
            amount = float(row["Amount"])
            if abs(amount) > 1_000_000:
                raise ValueError("Amount too large for Foo profile")


PROFILE = FooLenderProfile()
