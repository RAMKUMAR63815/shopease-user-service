from datetime import datetime
from typing import Literal

from pydantic import BaseModel
from pydantic import (
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.schemas.user_schema import (
    InputSchema,
    normalize_phone_number,
)

# Supported address categories
AddressType = Literal[
    "HOME",
    "OFFICE",
    "OTHER",
]


# Common address request fields
class UserAddressFields(InputSchema):

    address_type: AddressType

    full_name: str = Field(
        min_length=2,
        max_length=150,
    )

    phone_number: str = Field(
        min_length=7,
        max_length=20,
    )

    address_line_1: str = Field(
        min_length=3,
        max_length=255,
    )

    address_line_2: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str = Field(
        min_length=2,
        max_length=100,
    )

    state: str = Field(
        min_length=2,
        max_length=100,
    )

    country: str = Field(
        min_length=2,
        max_length=100,
    )

    postal_code: str = Field(
        min_length=3,
        max_length=20,
    )

    is_default: bool = False

    @field_validator("address_type", mode="before")
    @classmethod
    def normalize_address_type(cls, value):
        if isinstance(value, str):
            return value.strip().upper()

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value):
        return normalize_phone_number(value)

    @field_validator(
        "full_name",
        "address_line_1",
        "city",
        "state",
        "country",
        "postal_code",
    )
    @classmethod
    def validate_required_text(cls, value):
        if not value.strip():
            raise ValueError("This field cannot be empty")

        return value

    @field_validator("address_line_2")
    @classmethod
    def normalize_address_line_2(cls, value):
        if value is not None and not value.strip():
            return None

        return value


# Add a new address
class UserAddressCreate(UserAddressFields):
    pass


# Update an existing address (PUT)
class UserAddressUpdate(UserAddressFields):
    pass


# Address response
class UserAddressResponse(BaseModel):

    id: int

    address_type: str
    full_name: str
    phone_number: str

    address_line_1: str
    address_line_2: str | None = None

    city: str
    state: str
    country: str
    postal_code: str

    is_default: bool

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserAddressPatch(UserAddressUpdate):
    """Schema for updating only the supplied address fields."""

    address_type: AddressType | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone_number: str | None = None
    address_line_1: str | None = Field(default=None, min_length=1, max_length=255)
    address_line_2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, min_length=1, max_length=20)
    is_default: bool | None = None

    @model_validator(mode="after")
    def validate_patch(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        # Required database fields cannot be set to null.
        required_fields = {
            "address_type",
            "full_name",
            "phone_number",
            "address_line_1",
            "city",
            "state",
            "country",
            "postal_code",
            "is_default",
        }

        for field in required_fields:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self
