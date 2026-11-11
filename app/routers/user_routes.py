from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.security import CurrentUser
from app.schemas.user_schema import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfilePatch,
    UserProfileResponse,
)
from app.services import (
    UserServiceError,
    create_user_profile,
    get_user_profile,
    update_user_profile,
    patch_user_profile,
    delete_user_profile,
    deactivate_user_profile,
)

router = APIRouter(
    prefix="/api/users",
    tags=["User Profiles"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]

def handle_service_error(exc: UserServiceError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail=exc.detail,
    )

# --------------------------------------------------
# 1. CREATE PROFILE
# --------------------------------------------------

@router.post(
    "/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    data: UserProfileCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return create_user_profile(
            db=db,
            auth_user_id=current_user.auth_user_id,
            data=data,
        )

    except UserServiceError as exc:
        handle_service_error(exc)

# --------------------------------------------------
# 2. GET CURRENT USER PROFILE
# --------------------------------------------------

@router.get(
    "/profile",
    response_model=UserProfileResponse,
)
def get_profile(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return get_user_profile(
            db=db,
            auth_user_id=current_user.auth_user_id,
        )

    except UserServiceError as exc:
        handle_service_error(exc)

# --------------------------------------------------
# 3. UPDATE COMPLETE PROFILE
# --------------------------------------------------

@router.put(
    "/profile",
    response_model=UserProfileResponse,
)
def update_profile(
    data: UserProfileUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return update_user_profile(
            db=db,
            auth_user_id=current_user.auth_user_id,
            data=data,
        )

    except UserServiceError as exc:
        handle_service_error(exc)

# --------------------------------------------------
# 4. PARTIALLY UPDATE PROFILE
# --------------------------------------------------

@router.patch(
    "/profile",
    response_model=UserProfileResponse,
)
def patch_profile(
    data: UserProfilePatch,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return patch_user_profile(
            db=db,
            auth_user_id=current_user.auth_user_id,
            data=data,
        )

    except UserServiceError as exc:
        handle_service_error(exc)

# --------------------------------------------------
# 5. DELETE PROFILE
# --------------------------------------------------

@router.delete(
    "/profile",
    status_code=status.HTTP_200_OK,
)
def delete_profile(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return delete_user_profile(
            db=db,
            auth_user_id=current_user.auth_user_id,
        )

    except UserServiceError as exc:
        handle_service_error(exc)

# --------------------------------------------------
# 6. DEACTIVATE PROFILE
# --------------------------------------------------

@router.patch(
    "/profile/deactivate",
    status_code=status.HTTP_200_OK,
)
def deactivate_profile(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    try:
        return deactivate_user_profile(
            db=db,
            auth_user_id=current_user.auth_user_id,
        )

    except UserServiceError as exc:
        handle_service_error(exc)
