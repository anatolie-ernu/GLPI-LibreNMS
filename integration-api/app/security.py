from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, status

from .config import get_settings


def _require(expected: str, supplied: str | None) -> None:
    if not expected or not supplied or not hmac.compare_digest(expected, supplied):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid authentication",
        )


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    _require(get_settings().api_key, x_api_key)


def require_webhook_secret(
    x_webhook_secret: str | None = Header(default=None),
) -> None:
    _require(get_settings().webhook_secret, x_webhook_secret)
