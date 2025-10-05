from __future__ import annotations

from pathlib import Path
from typing import Optional


class StaticFiles:
    def __init__(self, directory: Path | str, html: bool = False) -> None:
        self.directory = Path(directory)
        self.html = html

    def __call__(self, *args, **kwargs):  # pragma: no cover - not used in tests
        raise NotImplementedError


__all__ = ["StaticFiles"]
