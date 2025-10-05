from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from statistics import mean
from typing import Dict, Iterable, List

from ..models import Transaction


@dataclass
class RecurringSeries:
    merchant: str
    average_amount: float
    average_interval_days: float
    occurrences: int


TOLERANCE = 4


def _days_between(dates: List[datetime]) -> List[int]:
    deltas: List[int] = []
    for idx in range(1, len(dates)):
        deltas.append((dates[idx] - dates[idx - 1]).days)
    return deltas


def detect_recurring(transactions: Iterable[Transaction]) -> Dict[str, RecurringSeries]:
    grouped: Dict[str, List[Transaction]] = defaultdict(list)
    for txn in transactions:
        key = txn.merchant or txn.description
        grouped[key].append(txn)

    recurring: Dict[str, RecurringSeries] = {}
    for key, txns in grouped.items():
        if len(txns) < 3:
            continue
        txns.sort(key=lambda t: t.date)
        deltas = _days_between([txn.date for txn in txns])
        if not deltas:
            continue
        avg_delta = mean(deltas)
        if min(deltas) < avg_delta - TOLERANCE or max(deltas) > avg_delta + TOLERANCE:
            continue
        avg_amount = mean(abs(txn.amount) for txn in txns)
        recurring[key] = RecurringSeries(
            merchant=key,
            average_amount=avg_amount,
            average_interval_days=avg_delta,
            occurrences=len(txns),
        )
    return recurring


__all__ = ["RecurringSeries", "detect_recurring"]
