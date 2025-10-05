from __future__ import annotations

from typing import Any, Dict

from .responses import HTMLResponse


class TemplateResponse(HTMLResponse):
    pass


class Jinja2Templates:
    def __init__(self, directory: str) -> None:
        self.directory = directory

    def TemplateResponse(self, name: str, context: Dict[str, Any]) -> HTMLResponse:
        return HTMLResponse(f"Template {name} rendered")


__all__ = ["Jinja2Templates", "TemplateResponse"]
