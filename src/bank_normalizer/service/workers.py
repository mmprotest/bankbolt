from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")

_executor = ThreadPoolExecutor(max_workers=4)


def submit(fn: Callable[..., T], *args, **kwargs) -> Future[T]:
    return _executor.submit(fn, *args, **kwargs)


def map_tasks(fn: Callable[[T], T], items: Iterable[T]) -> Iterable[T]:
    return _executor.map(fn, items)


__all__ = ["submit", "map_tasks"]
