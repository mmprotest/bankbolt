"""Lender profile registry."""

from importlib import import_module
from typing import Dict, Iterable, List, Protocol

from ...models import Transaction


class LenderProfile(Protocol):
    name: str

    def columns(self) -> List[str]:
        ...

    def transform(self, txn: Transaction) -> Dict[str, object]:
        ...

    def validate(self, rows: List[Dict[str, object]]) -> None:
        ...


def load_lender_profiles(config: Dict[str, Dict[str, str]]) -> Dict[str, LenderProfile]:
    profiles: Dict[str, LenderProfile] = {}
    for slug, entry in config.items():
        module = import_module(entry["module"])
        profile = getattr(module, "PROFILE")
        profiles[slug] = profile
    return profiles


__all__ = ["LenderProfile", "load_lender_profiles"]
