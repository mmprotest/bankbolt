from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class FieldInfo:
    default: Any = None
    default_factory: Optional[Callable[[], Any]] = None


def Field(*, default: Any = None, default_factory: Optional[Callable[[], Any]] = None) -> FieldInfo:
    return FieldInfo(default=default, default_factory=default_factory)


class BaseModel:
    model_config: Dict[str, Any] = {}

    def __init__(self, **data: Any) -> None:
        annotations = getattr(self, "__annotations__", {})
        for name, annotation in annotations.items():
            if name in data:
                value = data[name]
            else:
                attr = getattr(self.__class__, name, None)
                if isinstance(attr, FieldInfo):
                    if attr.default_factory is not None:
                        value = attr.default_factory()
                    else:
                        value = attr.default
                else:
                    value = attr
            setattr(self, name, value)

    def model_dump(self, mode: str | None = None) -> Dict[str, Any]:
        annotations = getattr(self, "__annotations__", {})
        return {name: getattr(self, name) for name in annotations}


__all__ = ["BaseModel", "Field"]
