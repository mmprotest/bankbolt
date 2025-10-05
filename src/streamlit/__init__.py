from __future__ import annotations

from typing import Any, Iterable, List


class _Widget:
    def __call__(self, *args: Any, **kwargs: Any) -> None:
        return None

    def __enter__(self):  # pragma: no cover
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover
        return False


def set_page_config(**kwargs: Any) -> None:
    return None


def title(text: str) -> None:
    return None


def sidebar():  # pragma: no cover
    class _Sidebar:
        def header(self, text: str) -> None:
            return None

        def text_input(self, label: str, value: str = "") -> str:
            return value

        def button(self, label: str) -> bool:
            return False

    return _Sidebar()


def file_uploader(label: str, type: Iterable[str], accept_multiple_files: bool = False):  # pragma: no cover
    return []


def dataframe(data: Any) -> None:
    return None


def columns(n: int):  # pragma: no cover
    return [_Widget() for _ in range(n)]


def button(label: str) -> bool:
    return False


def text_input(label: str, value: str = "") -> str:
    return value


def json(data: Any) -> None:
    return None


__all__ = [
    "set_page_config",
    "title",
    "sidebar",
    "file_uploader",
    "dataframe",
    "columns",
    "button",
    "text_input",
    "json",
]
