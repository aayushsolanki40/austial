"""``@Controller()`` and HTTP method decorators -- mirrors ``@nestjs/common``."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, TypeVar

from austial.core.metadata import (
    CONTROLLER_METADATA,
    HEADER_METADATA,
    HTTP_CODE_METADATA,
    ROUTE_METADATA,
    set_metadata,
)

T = TypeVar("T")


@dataclass
class ControllerMetadata:
    prefix: str = ""
    tags: Optional[list] = None


@dataclass
class RouteMetadata:
    method: str
    path: str = ""


def Controller(prefix: str = "", *, tags: Optional[list] = None) -> Callable[[T], T]:
    """Class decorator: declares a controller and its route prefix.

    Example::

        @Controller("health")
        class HealthController:
            def __init__(self, health_service: HealthService):
                self.health_service = health_service

            @Get()
            async def check(self):
                ...
    """
    prefix = "/" + prefix.strip("/") if prefix else ""

    def decorator(cls: T) -> T:
        set_metadata(CONTROLLER_METADATA, ControllerMetadata(prefix=prefix, tags=tags))(cls)
        return cls

    return decorator


def _route_decorator(method: str):
    def factory(path: str = "") -> Callable:
        normalized = "/" + path.strip("/") if path else ""

        def decorator(fn):
            set_metadata(ROUTE_METADATA, RouteMetadata(method=method, path=normalized))(fn)
            return fn

        return decorator

    return factory


Get = _route_decorator("GET")
Post = _route_decorator("POST")
Put = _route_decorator("PUT")
Patch = _route_decorator("PATCH")
Delete = _route_decorator("DELETE")
Options = _route_decorator("OPTIONS")
Head = _route_decorator("HEAD")


def HttpCode(status_code: int) -> Callable:
    """Method decorator overriding the default 2xx status code, mirrors
    Nest's ``@HttpCode()``."""

    def decorator(fn):
        set_metadata(HTTP_CODE_METADATA, status_code)(fn)
        return fn

    return decorator


def Header(key: str, value: str) -> Callable:
    """Method decorator adding a static response header, mirrors Nest's ``@Header()``.
    Stackable -- multiple ``@Header`` calls accumulate."""

    def decorator(fn):
        headers: Dict[str, str] = dict(getattr(fn, "__austial_metadata__", {}).get(HEADER_METADATA, {}))
        headers[key] = value
        set_metadata(HEADER_METADATA, headers)(fn)
        return fn

    return decorator
