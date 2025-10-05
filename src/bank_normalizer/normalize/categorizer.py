from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional

import yaml


class Categorizer:
    def __init__(self, path: Path) -> None:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        self.patterns: Dict[str, list[re.Pattern[str]]] = {}
        for category, entries in (data.get("categories") or {}).items():
            compiled = [re.compile(entry, re.IGNORECASE) for entry in entries]
            self.patterns[category] = compiled

    def categorize(self, description: str) -> Optional[str]:
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.search(description):
                    return category
        return None


__all__ = ["Categorizer"]
