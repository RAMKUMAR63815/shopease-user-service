from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import settings


# Store the verified identity returned by the Authentication Service
class AuthenticatedUser(BaseModel):

    auth_user_id: int = Field(gt=0)
    role: str = Field(min_length=1)

    model_config = ConfigDict(frozen=True)


# Read Bearer tokens from incoming API requests
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> AuthenticatedUser:

    """
    Validate the customer's JWT using the existing
    Authentication Service.

    Return the verified user ID and role.
    """

    # Reject requests without a Bearer token
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract the JWT
    access_token = credentials.credentials

    try:
        # Ask the Authentication Service to verify the JWT
        response = httpx.post(
            settings.auth_service_verify_url,
            json={
                "access_token": access_token,
            },
            timeout=settings.auth_service_timeout_seconds,
        )

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication Service timed out",
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication Service is unavailable",
        ) from exc

    # Handle authentication errors from Auth Service
    if response.status_code == 401:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # The Auth Service can reject inactive accounts
    if response.status_code == 403:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access is not permitted for this account",
        )

    # Handle server errors from Auth Service
    if response.status_code >= 500:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication Service encountered an error",
        )

    # Unexpected response status indicates an upstream issue
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected response from Authentication Service",
        )

    # Read the JSON response
    try:
        payload = response.json()

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from Authentication Service",
        ) from exc

    # Verify the response structure
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid authentication response",
        )

    # Reject a token that Auth Service did not validate
    if payload.get("valid") is not True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract the verified user ID and role
    user_id = payload.get("user_id")
    role = payload.get("role")

    # Ensure the user ID is a positive integer
    if type(user_id) is not int or user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid user identity from Authentication Service",
        )

    # Ensure the role is a non-empty string
    if not isinstance(role, str) or not role.strip():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid user role from Authentication Service",
        )

    # Return the verified customer identity
    return AuthenticatedUser(
        auth_user_id=user_id,
        role=role.strip(),
    )


# Reusable FastAPI dependency for protected endpoints
CurrentUser = Annotated[
    AuthenticatedUser,
    Depends(get_current_user),
]
