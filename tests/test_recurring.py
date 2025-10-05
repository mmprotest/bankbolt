from __future__ import annotations

from datetime import datetime, timedelta

from bank_normalizer.models import Transaction
from bank_normalizer.normalize.recurring import detect_recurring


def test_recurring_detection() -> None:
    base = datetime(2023, 1, 1)
    txns = []
    for i in range(4):
        txns.append(
            Transaction(
                id=str(i),
                date=base + timedelta(days=30 * i),
                description="RENT PAYMENT",
                merchant="RENT",
                debit=1200.0,
                credit=None,
                amount=-1200.0,
                balance=1000.0,
                category="RENT",
                account="1234",
                bank="ANZ",
                page=1,
                raw={}
            )
        )
    recurring = detect_recurring(txns)
    assert recurring
    series = next(iter(recurring.values()))
    assert series.occurrences == 4
    assert 25 < series.average_interval_days < 35
