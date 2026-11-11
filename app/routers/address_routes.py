
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.security import CurrentUser

from app.schemas.address_schema import (
    UserAddressCreate,
    UserAddressUpdate,
    UserAddressPatch,
    UserAddressResponse,
)

from app.services import (
    AddressServiceError,
    create_address,
    get_user_addresses,
    get_address,
    update_address,
    patch_address,
    delete_address,
    set_default_address,
)


router = APIRouter(
    prefix="/api/users/addresses",
    tags=["User Addresses"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


def handle_address_error(error: AddressServiceError):
    raise HTTPException(
        status_code=error.status_code,
        detail=error.detail,
    )


@router.post(
    "",
    response_model=UserAddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_address(
    data: UserAddressCreate,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    try:
        return create_address(
            db=db,
            auth_user_id=current_user.auth_user_id,
            data=data,
        )
    except AddressServiceError as error:
        handle_address_error(error)


@router.get(
    "",
    response_model=list[UserAddressResponse],
)
def read_user_addresses(
    db: DatabaseSession,
    current_user: CurrentUser,
):
    try:
        return get_user_addresses(
            db=db,
            auth_user_id=current_user.auth_user_id,
        )
    except AddressServiceError as error:
        handle_address_error(error)


@router.get(
    "/{address_id}",
    response_model=UserAddressResponse,
)
def read_user_address(
    address_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    try:
        return get_address(
            db=db,
            auth_user_id=current_user.auth_user_id,
            address_id=address_id,
        )
    except AddressServiceError as error:
        handle_address_error(error)


@router.put(
    "/{address_id}",
    response_model=UserAddressResponse,
)
def update_user_address(
    address_id: int,
    data: UserAddressUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    try:
        return update_address(
            db=db,
            auth_user_id=current_user.auth_user_id,
            address_id=address_id,
            data=data,
        )
    except AddressServiceError as error:
        handle_address_error(error)


@router.patch(
    "/{address_id}",
    response_model=UserAddressResponse,
)
def patch_user_address(
    address_id: int,
    data: UserAddressPatch,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    try:
        return patch_address(
            db=db,
            auth_user_id=current_user.auth_user_id,
            address_id=address_id,
            data=data,
        )
    except AddressServiceError as error:
        handle_address_error(error)


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
)
def remove_user_address(
    address_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    try:
        return delete_address(
            db=db,
            auth_user_id=current_user.auth_user_id,
            address_id=address_id,
        )
    except AddressServiceError as error:
        handle_address_error(error)


@router.patch(
    "/{address_id}/default",
    response_model=UserAddressResponse,
)
def make_default_address(
    address_id: int,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    try:
        return set_default_address(
            db=db,
            auth_user_id=current_user.auth_user_id,
            address_id=address_id,
        )
    except AddressServiceError as error:
        handle_address_error(error)
