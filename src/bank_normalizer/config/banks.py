from __future__ import annotations

from . import _load_yaml

DATA = _load_yaml("banks.yaml")
BANKS = DATA.get("banks", [])
