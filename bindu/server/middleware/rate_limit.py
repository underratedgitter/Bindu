"""Rate limiting middleware and utilities for HTTP endpoints."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

from bindu.settings import app_settings


def _merge_limits(*limits: str) -> str:
    """Merge multiple limit strings into a SlowAPI-compatible rule."""
    return ";".join(limit.strip() for limit in limits if limit and limit.strip())


DEFAULT_LIMIT_RULE = _merge_limits(
    app_settings.rate_limit.default_limit,
    app_settings.rate_limit.burst_limit,
)
A2A_LIMIT_RULE = _merge_limits(
    app_settings.rate_limit.a2a_limit,
    app_settings.rate_limit.burst_limit,
)
NEGOTIATION_LIMIT_RULE = _merge_limits(
    app_settings.rate_limit.negotiation_limit,
    app_settings.rate_limit.burst_limit,
)

limiter = Limiter(
    key_func=get_remote_address,
    enabled=app_settings.rate_limit.enabled,
    headers_enabled=True,
)


def limit_endpoint(limit_rule: str) -> Callable:
    """Apply rate limits only when a real Starlette Request is available.

    This preserves compatibility for direct unit tests that invoke endpoint
    callables with mocked request objects.
    """

    def decorator(func: Callable) -> Callable:
        limited_func = limiter.limit(limit_rule)(func)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            request = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not isinstance(request, Request):
                return await func(*args, **kwargs)

            return await limited_func(*args, **kwargs)

        return wrapper

    return decorator


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Return RFC-compliant 429 responses with Retry-After details."""
    retry_after = "1"
    if hasattr(exc, "headers") and isinstance(exc.headers, dict):
        retry_after = exc.headers.get("Retry-After") or retry_after

    response_headers = {"Retry-After": str(retry_after)}

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded: {exc.detail}",
            "retry_after": retry_after,
        },
        headers=response_headers,
    )
