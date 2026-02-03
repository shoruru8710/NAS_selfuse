"""Service token verification for EC2 -> NAS communication."""

import hmac

from fastapi import Header, HTTPException, status

from app.config import settings


def verify_token(token: str) -> bool:
    """Constant-time comparison of service token."""
    return hmac.compare_digest(token, settings.service_token)


async def require_service_token(
    x_service_token: str = Header(..., alias="X-Service-Token"),
) -> str:
    """FastAPI dependency to require valid service token."""
    if not verify_token(x_service_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing service token",
        )
    return x_service_token
