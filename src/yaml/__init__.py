from __future__ import annotations

import json
from typing import Any


def safe_load(stream: Any) -> Any:
    if hasattr(stream, "read"):
        content = stream.read()
    else:
        content = stream
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    return json.loads(content)


__all__ = ["safe_load"]
