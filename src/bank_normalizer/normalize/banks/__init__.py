"""Bank profile registry."""

from importlib import import_module
from typing import Dict, Iterable, List, Optional, Protocol

from ...extract.pdf_reader import PDFStatement


class BankProfile(Protocol):
    name: str

    def detect(self, statement: PDFStatement) -> float:
        """Return confidence score between 0 and 1."""

    def column_map(self) -> Dict[str, str]:
        """Return mapping for canonical columns."""

    def clean_description(self, value: str) -> str:
        ...


def load_bank_profiles(config: Iterable[Dict[str, object]]) -> List[BankProfile]:
    profiles: List[BankProfile] = []
    for entry in config:
        module_name = entry["module"]  # type: ignore[index]
        module = import_module(str(module_name))
        profile = getattr(module, "PROFILE")
        profiles.append(profile)
    return profiles


def select_bank_profile(statement: PDFStatement, profiles: Iterable[BankProfile]) -> Optional[BankProfile]:
    best_score = 0.0
    best_profile: Optional[BankProfile] = None
    for profile in profiles:
        score = profile.detect(statement)
        if score > best_score:
            best_score = score
            best_profile = profile
    return best_profile


__all__ = ["BankProfile", "load_bank_profiles", "select_bank_profile"]
