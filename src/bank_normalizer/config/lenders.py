from __future__ import annotations

from . import _load_yaml

DATA = _load_yaml("lenders.yaml")
LENDERS = DATA.get("lenders", {})
