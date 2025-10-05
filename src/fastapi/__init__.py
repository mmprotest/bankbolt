from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from .responses import FileResponse, HTMLResponse, JSONResponse


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str = "") -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class Depends:
    def __init__(self, dependency: Callable[..., Any]) -> None:
        self.dependency = dependency


class File:
    def __init__(self, default: Any = None) -> None:
        self.default = default


class Request:
    def __init__(self, headers: Optional[Dict[str, str]] = None) -> None:
        self.headers = headers or {}


class UploadFile:
    def __init__(self, filename: str, data: bytes) -> None:
        self.filename = filename
        self._data = data

    async def read(self) -> bytes:
        return self._data


@dataclass
class Route:
    path: str
    method: str
    endpoint: Callable[..., Any]


class FastAPI:
    def __init__(self, title: str | None = None) -> None:
        self.title = title or "FastAPI"
        self.routes: List[Route] = []
        self.mounts: List[Any] = []

    def add_api_route(self, path: str, endpoint: Callable[..., Any], methods: List[str]) -> None:
        for method in methods:
            self.routes.append(Route(path=path, method=method.upper(), endpoint=endpoint))

    def get(self, path: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, ["GET"])
            return func

        return decorator

    def post(self, path: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, ["POST"])
            return func

        return decorator

    def mount(self, path: str, app: Any, name: Optional[str] = None) -> None:
        self.mounts.append((path, app, name))


def _match(path: str, template: str) -> Optional[Dict[str, str]]:
    path_parts = [p for p in path.strip("/").split("/") if p]
    template_parts = [p for p in template.strip("/").split("/") if p]
    if len(path_parts) != len(template_parts):
        return None
    params: Dict[str, str] = {}
    for part, template_part in zip(path_parts, template_parts):
        if template_part.startswith("{") and template_part.endswith("}"):
            params[template_part[1:-1]] = part
        elif part != template_part:
            return None
    return params


class ResponseWrapper:
    def __init__(self, status_code: int, body: Any) -> None:
        self.status_code = status_code
        self._body = body

    def json(self) -> Any:
        return self._body

    @property
    def content(self) -> bytes:
        if isinstance(self._body, bytes):
            return self._body
        if isinstance(self._body, str):
            return self._body.encode("utf-8")
        return str(self._body).encode("utf-8")


class TestClient:
    def __init__(self, app: FastAPI) -> None:
        self.app = app

    def _call(self, method: str, path: str, *, files: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> ResponseWrapper:
        for route in self.app.routes:
            params = _match(path, route.path)
            if params is None or route.method != method.upper():
                continue
            request = Request(headers=headers)
            try:
                result = self._execute(route.endpoint, request, params, files)
            except HTTPException as exc:
                return ResponseWrapper(exc.status_code, exc.detail)
            if isinstance(result, (JSONResponse, HTMLResponse, FileResponse)):
                return ResponseWrapper(result.status_code, result.body)
            return ResponseWrapper(200, result)
        raise HTTPException(404, "Not found")

    def _execute(self, endpoint: Callable[..., Any], request: Request, params: Dict[str, str], files: Optional[Dict[str, Any]]) -> Any:
        sig = inspect.signature(endpoint)
        kwargs: Dict[str, Any] = {}
        uploads: List[UploadFile] = []
        if files:
            for value in files.values():
                if isinstance(value, tuple):
                    filename, fileobj, _content_type = value
                    data = fileobj.read()
                    uploads.append(UploadFile(filename, data))
        for name, parameter in sig.parameters.items():
            if isinstance(parameter.default, Depends):
                dependency = parameter.default.dependency
                dep_result = dependency(request)
                kwargs[name] = dep_result
            elif name == "request":
                kwargs[name] = request
            elif name == "files":
                kwargs[name] = uploads
            elif name in params:
                kwargs[name] = params[name]
            else:
                kwargs[name] = None
        result = endpoint(**kwargs)
        if inspect.iscoroutine(result):
            return asyncio.run(result)
        return result

    def get(self, path: str, headers: Optional[Dict[str, str]] = None) -> ResponseWrapper:
        return self._call("GET", path, headers=headers)

    def post(self, path: str, files: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> ResponseWrapper:
        return self._call("POST", path, files=files, headers=headers)


__all__ = [
    "FastAPI",
    "Depends",
    "File",
    "HTTPException",
    "Request",
    "UploadFile",
    "TestClient",
]
