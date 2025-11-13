from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.config import settings

security = HTTPBearer()

VALID_API_TOKENS = (
    {settings.API_ACCESS_TOKEN: {"name": "Frontend App", "permissions": ["read", "write"]}}
    if settings.API_ACCESS_TOKEN
    else {}
)


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies API token unless authentication is disabled.
    """
    if not settings.ENABLE_TOKEN_AUTH:
        return {"name": "Anonymous", "permissions": ["read", "write"], "auth_disabled": True}

    token = credentials.credentials

    if token not in VALID_API_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return VALID_API_TOKENS[token]
