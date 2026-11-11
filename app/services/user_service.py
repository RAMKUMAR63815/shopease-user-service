from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user_model import UserProfile
from app.schemas.user_schema import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfilePatch,
)


# Custom exception for profile business logic
class UserServiceError(Exception):

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

        super().__init__(detail) #Initializes the standard exception message    super()parent class


# --------------------------------------------------
# COMMON PROFILE LOOKUP
# --------------------------------------------------

def get_profile_by_auth_user_id(
    db: Session,
    auth_user_id: int,
) -> UserProfile:
    """
    Find a profile using the verified Authentication
    Service user ID.
    """

    profile = db.scalar(
        select(UserProfile).where(
            UserProfile.auth_user_id == auth_user_id
        )
    )

    if profile is None:
        raise UserServiceError(
            404,
            "User profile not found",
        )

    # Deactivated profiles cannot use normal profile operations
    if not profile.is_active:
        raise UserServiceError(
            403,
            "User profile is inactive",
        )

    return profile


# --------------------------------------------------
# 1. CREATE USER PROFILE
# --------------------------------------------------

def create_user_profile(
    db: Session,
    auth_user_id: int,
    data: UserProfileCreate,
) -> UserProfile:
    """
    Create a profile for the authenticated user.

    The auth_user_id comes from the verified JWT identity,
    not from the customer's request body.
    """

    # Check whether the authenticated user already has a profile
    existing_profile = db.scalar(
        select(UserProfile).where(
            UserProfile.auth_user_id == auth_user_id
        )
    )

    if existing_profile is not None:
        raise UserServiceError(
            409,
            "A profile already exists for this user",
        )

    # Create a new local profile
    profile = UserProfile(
        auth_user_id=auth_user_id,
        **data.model_dump(), #Pydantic v2 method that converts a Pydantic model object into a normal Python dictionary (dict).
    )

    try:
        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile

    except IntegrityError as exc:
        # Handle duplicate requests or concurrent profile creation
        db.rollback()

        raise UserServiceError(
            409,
            "A profile already exists for this user",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()

        raise UserServiceError(
            500,
            "Database error while creating user profile",
        ) from exc


# --------------------------------------------------
# 2. GET CURRENT USER PROFILE
# --------------------------------------------------

def get_user_profile(
    db: Session,
    auth_user_id: int,
) -> UserProfile:
    """
    Retrieve only the authenticated user's profile.
    """

    return get_profile_by_auth_user_id(
        db,
        auth_user_id,
    )


# --------------------------------------------------
# 3. UPDATE COMPLETE USER PROFILE
# --------------------------------------------------

def update_user_profile(
    db: Session,
    auth_user_id: int,
    data: UserProfileUpdate,
) -> UserProfile:
    """
    Replace the editable profile fields.

    All fields required by the PUT request schema
    must be provided by the client.
    """

    profile = get_profile_by_auth_user_id(
        db,
        auth_user_id,
    )

    # Get all editable profile fields
    update_data = data.model_dump()

    try:
        # Update each profile field
        for field, value in update_data.items():
            setattr(profile, field, value)

        db.commit()
        db.refresh(profile)

        return profile

    except SQLAlchemyError as exc:
        db.rollback()

        raise UserServiceError(
            500,
            "Database error while updating user profile",
        ) from exc


# --------------------------------------------------
# 4. PARTIALLY UPDATE USER PROFILE
# --------------------------------------------------

def patch_user_profile(
    db: Session,
    auth_user_id: int,
    data: UserProfilePatch,
) -> UserProfile:
    """
    Update only the fields supplied by the customer.

    Existing values of omitted fields are preserved.
    """

    profile = get_profile_by_auth_user_id(
        db,
        auth_user_id,
    )

    # Include only fields submitted by the client
    update_data = data.model_dump(
        exclude_unset=True,
    )

    if not update_data:
        raise UserServiceError(
            422,
            "At least one profile field must be provided",
        )

    try:
        # Update only submitted fields
        for field, value in update_data.items():
            setattr(profile, field, value)

        db.commit()
        db.refresh(profile)

        return profile

    except SQLAlchemyError as exc:
        db.rollback()

        raise UserServiceError(
            500,
            "Database error while partially updating profile",
        ) from exc


# --------------------------------------------------
# 5. DELETE USER PROFILE
# --------------------------------------------------

def delete_user_profile(
    db: Session,
    auth_user_id: int,
) -> dict:
    """
    Delete the authenticated user's local profile.

    The database relationship handles deletion of
    the profile's associated addresses.

    This does not delete the Authentication Service account.
    """

    profile = get_profile_by_auth_user_id(
        db,
        auth_user_id,
    )

    try:
        db.delete(profile)
        db.commit()

        return {
            "message": "User profile deleted successfully"
        }

    except SQLAlchemyError as exc:
        db.rollback()

        raise UserServiceError(
            500,
            "Database error while deleting user profile",
        ) from exc


# --------------------------------------------------
# 6. DEACTIVATE USER PROFILE
# --------------------------------------------------

def deactivate_user_profile(
    db: Session,
    auth_user_id: int,
) -> dict:
    """
    Deactivate the local User Service profile.

    Do not delete or deactivate the account in
    the Authentication Service.
    """

    profile = get_profile_by_auth_user_id(
        db,
        auth_user_id,
    )

    try:
        profile.is_active = False

        db.commit()
        db.refresh(profile)

        return {
            "message": "User profile deactivated successfully"
        }

    except SQLAlchemyError as exc:
        db.rollback()

        raise UserServiceError(
            500,
            "Database error while deactivating user profile",
        ) from exc
