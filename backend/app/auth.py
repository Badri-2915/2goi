"""
Authentication Module — JWT token verification and user management.

This module handles:
1. JWT Token Verification: Validates Supabase auth tokens
   - Primary: ES256 algorithm via JWKS endpoint (modern Supabase tokens)
   - Fallback: HS256 algorithm with JWT secret (legacy tokens)
2. User Management: Auto-creates users in our DB on first API request
3. Auth Dependencies: FastAPI dependency injection for protected routes

Flow when a request comes in with a Bearer token:
  1. Extract token from Authorization header
  2. Verify signature using Supabase's public keys (JWKS)
  3. Extract user_id (sub claim) from the token payload
  4. Look up user in our DB; create if first time
  5. Return the User object to the route handler
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt as pyjwt
from jwt import PyJWKClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.database import get_db
from app.models.user import User

settings = get_settings()

# HTTPBearer with auto_error=False allows unauthenticated requests to pass through
# (for endpoints that work for both anonymous and logged-in users)
security = HTTPBearer(auto_error=False)

# JWKS client fetches Supabase's public signing keys for ES256 verification
# Keys are cached automatically by the PyJWKClient
_jwks_client = PyJWKClient(f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json")


async def verify_token(token: str) -> dict:
    """
    Verify a Supabase JWT token and return its payload.

    Tries ES256 (JWKS) first, falls back to HS256 (JWT secret).
    Raises HTTP 401 if both methods fail.
    """
    try:
        # Try ES256 verification via JWKS first (modern Supabase tokens)
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = pyjwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )
        return payload
    except Exception:
        pass

    # Fallback to HS256 verification with JWT secret (legacy Supabase tokens)
    try:
        payload = pyjwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except pyjwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    FastAPI dependency: Get the current user from the JWT token.
    Returns None if no token is provided (for anonymous access).
    Auto-creates user in our DB on first login.
    """
    if not credentials:
        return None

    payload = await verify_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Check if user exists in our DB; create on first login (just-in-time provisioning)
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        email = payload.get("email", "")
        user = User(id=UUID(user_id), email=email, plan="free")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency: Require authentication. Returns 401 if not logged in."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user = await get_current_user(credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user


def get_client_ip(request: Request) -> str:
    """Extract the real client IP from the request (handles reverse proxies like Render)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
