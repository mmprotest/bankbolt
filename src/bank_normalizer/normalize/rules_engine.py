from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional

try:  # pragma: no cover - optional dependency
    from rapidfuzz import fuzz  # type: ignore
except Exception:
    from difflib import SequenceMatcher

    class _FallbackFuzz:
        @staticmethod
        def partial_ratio(a: str, b: str) -> int:
            if not a or not b:
                return 0
            ratio = SequenceMatcher(None, a, b).ratio()
            return int(ratio * 100)

    fuzz = _FallbackFuzz()

from ..models import Transaction
from ..extract.parse_table import ParsedRow, parse_date
from .banks import BankProfile

AMOUNT_CLEAN_RE = re.compile(r"[^0-9.-]")


@dataclass
class NormalizedRow:
    date: datetime
    description: str
    merchant: Optional[str]
    debit: Optional[float]
    credit: Optional[float]
    amount: float
    balance: Optional[float]
    page: int
    raw: Dict[str, str]


def _parse_amount(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    negative = cleaned.startswith("-") or cleaned.startswith("(")
    cleaned = cleaned.replace("(", "").replace(")", "")
    cleaned = AMOUNT_CLEAN_RE.sub("", cleaned)
    if cleaned in {"", "-", "."}:
        return None
    try:
        amount = float(cleaned)
    except ValueError:
        return None
    if negative and amount > 0:
        amount = -amount
    return amount


def _infer_merchant(description: str, candidates: Iterable[str]) -> Optional[str]:
    best_score = 0
    best_match: Optional[str] = None
    for candidate in candidates:
        score = fuzz.partial_ratio(description.upper(), candidate.upper())
        if score > best_score:
            best_score = score
            best_match = candidate
    if best_score < 70:
        return None
    return best_match


KNOWN_MERCHANTS = [
    "WOOLWORTHS",
    "COLES",
    "ALDI",
    "BUNNINGS",
    "AFTERPAY",
    "ZIP PAY",
    "TELSTRA",
    "OPTUS",
    "PAYPAL",
]


def normalize_rows(rows: Iterable[ParsedRow], bank: BankProfile, bank_name: str) -> List[NormalizedRow]:
    normalized: List[NormalizedRow] = []
    for row in rows:
        raw = row.raw
        date_value = None
        for key in ("Date", "Transaction Date"):
            if key in raw:
                date_value = raw[key]
                break
        if not date_value:
            continue
        parsed = parse_date(date_value)
        if not parsed:
            continue
        description = raw.get("Description") or raw.get("Details") or ""
        description = bank.clean_description(description)
        debit = _parse_amount(raw.get("Debit") or raw.get("Withdrawal") or raw.get("Withdrawals"))
        credit = _parse_amount(raw.get("Credit") or raw.get("Deposit") or raw.get("Deposits"))
        balance = _parse_amount(raw.get("Balance"))
        amount = 0.0
        if debit is not None:
            amount -= abs(debit)
        if credit is not None:
            amount += abs(credit)
        if amount == 0.0 and raw.get("Amount"):
            amt = _parse_amount(raw.get("Amount"))
            if amt is not None:
                amount = amt
                if amount < 0:
                    debit = abs(amount)
                    credit = None
                else:
                    credit = amount
                    debit = None
        merchant = _infer_merchant(description, KNOWN_MERCHANTS)
        normalized.append(
            NormalizedRow(
                date=parsed,
                description=description,
                merchant=merchant,
                debit=abs(debit) if debit is not None else None,
                credit=abs(credit) if credit is not None else None,
                amount=amount,
                balance=balance,
                page=row.page,
                raw=raw,
            )
        )
    return normalized


def to_transactions(rows: Iterable[NormalizedRow], bank_name: str) -> List[Transaction]:
    transactions: List[Transaction] = []
    for index, row in enumerate(rows):
        identifier_src = f"{bank_name}-{row.page}-{index}-{row.description}-{row.amount}-{row.date.isoformat()}"
        identifier = hashlib.sha1(identifier_src.encode()).hexdigest()[:16]
        debit = row.debit if row.amount < 0 else None
        credit = row.credit if row.amount > 0 else None
        transactions.append(
            Transaction(
                id=identifier,
                date=row.date,
                description=row.description,
                merchant=row.merchant,
                debit=debit,
                credit=credit,
                amount=row.amount,
                balance=row.balance,
                category=None,
                account=None,
                bank=bank_name,
                page=row.page,
                raw=row.raw,
            )
        )
    return transactions


__all__ = ["NormalizedRow", "normalize_rows", "to_transactions"]
