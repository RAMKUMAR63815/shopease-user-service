
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user_model import UserProfile
from app.models.address_model import UserAddress

from app.schemas.address_schema import (
    UserAddressCreate,
    UserAddressUpdate,
    UserAddressPatch,
)


class AddressServiceError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


# --------------------------------------------------
# COMMON PROFILE LOOKUP
# --------------------------------------------------

def get_active_profile(
    db: Session,
    auth_user_id: int,
    lock: bool = False,
) -> UserProfile:

    statement = select(UserProfile).where(
        UserProfile.auth_user_id == auth_user_id
    )

    if lock:
        statement = statement.with_for_update()

    profile = db.scalar(statement)

    if profile is None:
        raise AddressServiceError(404, "User profile not found")

    if not profile.is_active:
        raise AddressServiceError(403, "User profile is inactive")

    return profile


# --------------------------------------------------
# COMMON ADDRESS OWNERSHIP CHECK
# --------------------------------------------------

def get_owned_address(
    db: Session,
    address_id: int,
    profile_id: int,
) -> UserAddress:

    address = db.scalar(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_id == profile_id,
        )
    )

    if address is None:
        raise AddressServiceError(404, "Address not found")

    return address


# --------------------------------------------------
# COMMON DEFAULT ADDRESS HELPER
# --------------------------------------------------

def clear_other_default_addresses(
    db: Session,
    profile_id: int,
    exclude_address_id: int | None = None,
) -> None:

    statement = update(UserAddress).where(
        UserAddress.user_id == profile_id
    )

    if exclude_address_id is not None:
        statement = statement.where(
            UserAddress.id != exclude_address_id
        )

    db.execute(statement.values(is_default=False))


def select_replacement_default(
    db: Session,
    profile_id: int,
    exclude_address_id: int,
) -> None:

    replacement = db.scalar(
        select(UserAddress)
        .where(
            UserAddress.user_id == profile_id,
            UserAddress.id != exclude_address_id,
        )
        .order_by(UserAddress.id.asc())
        .limit(1)
    )

    if replacement is not None:
        replacement.is_default = True


# --------------------------------------------------
# 1. CREATE ADDRESS
# --------------------------------------------------

def create_address(
    db: Session,
    auth_user_id: int,
    data: UserAddressCreate,
) -> UserAddress:

    try:
        profile = get_active_profile(db, auth_user_id, lock=True)

        address_data = data.model_dump()

        if address_data["is_default"]:
            clear_other_default_addresses(db, profile.id)

        new_address = UserAddress(
            user_id=profile.id,
            **address_data,
        )

        db.add(new_address)
        db.commit()
        db.refresh(new_address)

        return new_address

    except AddressServiceError:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        db.rollback()
        raise AddressServiceError(
            500,
            "Database error while creating address",
        ) from exc


# --------------------------------------------------
# 2. LIST USER ADDRESSES
# --------------------------------------------------

def get_user_addresses(
    db: Session,
    auth_user_id: int,
) -> list[UserAddress]:

    profile = get_active_profile(db, auth_user_id)

    statement = (
        select(UserAddress)
        .where(UserAddress.user_id == profile.id)
        .order_by(
            UserAddress.is_default.desc(),
            UserAddress.id.asc(),
        )
    )

    return list(db.scalars(statement).all())


# --------------------------------------------------
# 3. GET ONE ADDRESS
# --------------------------------------------------

def get_address(
    db: Session,
    auth_user_id: int,
    address_id: int,
) -> UserAddress:

    profile = get_active_profile(db, auth_user_id)

    return get_owned_address(
        db,
        address_id,
        profile.id,
    )


# --------------------------------------------------
# 4. UPDATE COMPLETE ADDRESS (PUT)
# --------------------------------------------------

def update_address(
    db: Session,
    auth_user_id: int,
    address_id: int,
    data: UserAddressUpdate,
) -> UserAddress:

    try:
        profile = get_active_profile(db, auth_user_id, lock=True)

        address = get_owned_address(
            db,
            address_id,
            profile.id,
        )

        previous_default = address.is_default
        update_data = data.model_dump()

        if update_data["is_default"]:
            clear_other_default_addresses(
                db,
                profile.id,
                exclude_address_id=address_id,
            )

        for field, value in update_data.items():
            setattr(address, field, value)

        if previous_default and not address.is_default:
            select_replacement_default(
                db,
                profile.id,
                address_id,
            )

        db.commit()
        db.refresh(address)

        return address

    except AddressServiceError:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        db.rollback()
        raise AddressServiceError(
            500,
            "Database error while updating address",
        ) from exc


# --------------------------------------------------
# 5. PARTIAL UPDATE ADDRESS (PATCH)
# --------------------------------------------------

def patch_address(
    db: Session,
    auth_user_id: int,
    address_id: int,
    data: UserAddressPatch,
) -> UserAddress:

    try:
        profile = get_active_profile(db, auth_user_id, lock=True)

        address = get_owned_address(
            db,
            address_id,
            profile.id,
        )

        previous_default = address.is_default

        # Only take fields supplied in the PATCH request.
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise AddressServiceError(
                422,
                "At least one field must be provided",
            )

        requested_default = update_data.get(
            "is_default",
            address.is_default,
        )

        # If this address becomes default, clear the others.
        if requested_default is True:
            clear_other_default_addresses(
                db,
                profile.id,
                exclude_address_id=address_id,
            )

        # Update only supplied fields.
        for field, value in update_data.items():
            setattr(address, field, value)

        # If the current default is removed, choose a replacement.
        if previous_default and requested_default is False:
            select_replacement_default(
                db,
                profile.id,
                address_id,
            )

        db.commit()
        db.refresh(address)

        return address

    except AddressServiceError:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        db.rollback()
        raise AddressServiceError(
            500,
            "Database error while partially updating address",
        ) from exc


# --------------------------------------------------
# 6. DELETE ADDRESS
# --------------------------------------------------

def delete_address(
    db: Session,
    auth_user_id: int,
    address_id: int,
) -> dict:

    try:
        profile = get_active_profile(db, auth_user_id, lock=True)

        address = get_owned_address(
            db,
            address_id,
            profile.id,
        )

        was_default = address.is_default

        db.delete(address)

        if was_default:
            select_replacement_default(
                db,
                profile.id,
                address_id,
            )

        db.commit()

        return {
            "message": "Address deleted successfully",
            "address_id": address_id,
        }

    except AddressServiceError:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        db.rollback()
        raise AddressServiceError(
            500,
            "Database error while deleting address",
        ) from exc


# --------------------------------------------------
# 7. SET DEFAULT ADDRESS
# --------------------------------------------------

def set_default_address(
    db: Session,
    auth_user_id: int,
    address_id: int,
) -> UserAddress:

    try:
        profile = get_active_profile(db, auth_user_id, lock=True)

        address = get_owned_address(
            db,
            address_id,
            profile.id,
        )

        clear_other_default_addresses(
            db,
            profile.id,
            exclude_address_id=address_id,
        )

        address.is_default = True

        db.commit()
        db.refresh(address)

        return address

    except AddressServiceError:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        db.rollback()
        raise AddressServiceError(
            500,
            "Database error while setting default address",
        ) from exc
