from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JSONResponse:
    def __init__(self, content: Any, status_code: int = 200) -> None:
        self.body = content
        self.status_code = status_code

    def json(self) -> Any:  # pragma: no cover - compatibility
        return self.body


class HTMLResponse:
    def __init__(self, content: str, status_code: int = 200) -> None:
        self.body = content
        self.status_code = status_code


class FileResponse:
    def __init__(self, path: Path, status_code: int = 200) -> None:
        self.path = Path(path)
        self.status_code = status_code
        self.body = self.path.read_bytes()


__all__ = ["JSONResponse", "HTMLResponse", "FileResponse"]
