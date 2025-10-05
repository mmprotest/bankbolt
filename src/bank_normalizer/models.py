from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """Normalized transaction entry."""

    id: str
    date: datetime
    description: str
    merchant: Optional[str] = None
    debit: Optional[float] = None
    credit: Optional[float] = None
    amount: float
    balance: Optional[float] = None
    category: Optional[str] = None
    account: Optional[str] = None
    bank: str
    page: Optional[int] = None
    raw: Dict[str, Any] = Field(default_factory=dict)

    model_config = dict(frozen=True)


class StatementMeta(BaseModel):
    """Metadata for a processed statement."""

    bank: str
    account_last4: Optional[str] = None
    currency: str = "AUD"
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    pages: int
    warnings: List[str] = Field(default_factory=list)


class ResultBundle(BaseModel):
    """Bundle returned from normalization."""

    meta: StatementMeta
    transactions: List[Transaction]
    liabilities: Dict[str, Any]
    summary: Dict[str, Any]

    def to_json(self) -> str:
        try:
            import orjson
        except Exception:  # pragma: no cover - optional dependency
            import json

            return json.dumps(self.model_dump(mode="json"), default=str)
        else:
            return orjson.dumps(self.model_dump(mode="json"), option=orjson.OPT_INDENT_2).decode()


__all__ = ["Transaction", "StatementMeta", "ResultBundle"]
