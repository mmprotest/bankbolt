from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Iterable

from ..models import Transaction
from ..normalize.recurring import RecurringSeries

LIABILITY_KEYWORDS = {
    "rent": ["RENT"],
    "bnpl": ["AFTERPAY", "ZIP"],
    "child_support": ["CHILD SUPPORT"],
    "loans": ["LOAN", "FINANCE"],
}

FEE_KEYWORDS = ["FEE", "OVERDRAWN", "NSF"]


def _matches_keywords(description: str, keywords: Iterable[str]) -> bool:
    upper = description.upper()
    return any(keyword in upper for keyword in keywords)


def compute_liabilities(transactions: Iterable[Transaction]) -> Dict[str, float]:
    totals: Dict[str, float] = {key: 0.0 for key in LIABILITY_KEYWORDS}
    for txn in transactions:
        if txn.amount >= 0:
            continue
        for key, keywords in LIABILITY_KEYWORDS.items():
            if _matches_keywords(txn.description, keywords) or (txn.category and txn.category.upper() == key.upper()):
                totals[key] += abs(txn.amount)
    return totals


def compute_fee_flags(transactions: Iterable[Transaction]) -> Dict[str, int]:
    counts = Counter()
    for txn in transactions:
        if _matches_keywords(txn.description, FEE_KEYWORDS):
            counts["fees"] += 1
        if "NSF" in txn.description.upper() or "OVERDRAWN" in txn.description.upper():
            counts["nsf"] += 1
    return counts


def monthly_totals(transactions: Iterable[Transaction]) -> Dict[str, float]:
    totals: Dict[str, float] = defaultdict(float)
    for txn in transactions:
        month = txn.date.strftime("%Y-%m")
        totals[month] += txn.amount
    return dict(totals)


def build_summary(transactions: Iterable[Transaction], recurring: Dict[str, RecurringSeries]) -> Dict[str, object]:
    txns = list(transactions)
    if not txns:
        return {"totals": {}, "liabilities": {}, "recurring": {}, "fees": {}}
    liabilities = compute_liabilities(txns)
    fees = compute_fee_flags(txns)
    recurring_summary = {
        key: {
            "average_amount": series.average_amount,
            "occurrences": series.occurrences,
            "interval_days": series.average_interval_days,
        }
        for key, series in recurring.items()
    }
    return {
        "totals": monthly_totals(txns),
        "liabilities": liabilities,
        "recurring": recurring_summary,
        "fees": dict(fees),
    }


__all__ = ["build_summary", "compute_liabilities"]
