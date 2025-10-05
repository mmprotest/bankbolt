from __future__ import annotations

from datetime import datetime
from typing import Any, Optional


def parse(value: str, settings: Optional[dict[str, Any]] = None) -> Optional[datetime]:
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


__all__ = ["parse"]
