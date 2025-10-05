from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Sequence

import yaml

from .extract import parse_statement_rows, read_pdf
from .models import ResultBundle, StatementMeta, Transaction
from .normalize import Categorizer, normalize_rows
from .normalize.banks import load_bank_profiles, select_bank_profile
from .normalize.rules_engine import to_transactions
from .normalize.recurring import detect_recurring
from .export.summary import build_summary

CONFIG_DIR = Path(__file__).resolve().parent / "config"


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _load_bank_profiles() -> Sequence:
    config = _load_yaml(CONFIG_DIR / "banks.yaml")
    return load_bank_profiles(config.get("banks", []))


def _categorizer() -> Categorizer:
    return Categorizer(CONFIG_DIR / "categories.yaml")


def normalize_pdfs(paths: Iterable[Path | str]) -> List[ResultBundle]:
    profiles = _load_bank_profiles()
    categorizer = _categorizer()
    bundles: List[ResultBundle] = []
    for path in paths:
        statement = read_pdf(Path(path))
        profile = select_bank_profile(statement, profiles)
        bank_name = profile.name if profile else "Unknown"
        rows = parse_statement_rows(statement)
        if profile:
            normalized_rows = normalize_rows(rows, profile, bank_name)
        else:
            normalized_rows = []
        transactions = to_transactions(normalized_rows, bank_name)
        for txn in transactions:
            txn.category = categorizer.categorize(txn.description)
        recurring = detect_recurring(transactions)
        summary = build_summary(transactions, recurring)
        meta = StatementMeta(
            bank=bank_name,
            account_last4=None,
            currency="AUD",
            period_start=min((txn.date.date() for txn in transactions), default=None),
            period_end=max((txn.date.date() for txn in transactions), default=None),
            pages=len(statement.pages),
            warnings=["No transactions detected"] if not transactions else [],
        )
        bundles.append(
            ResultBundle(
                meta=meta,
                transactions=transactions,
                liabilities=summary.get("liabilities", {}),
                summary=summary,
            )
        )
    return bundles


__all__ = ["normalize_pdfs"]
