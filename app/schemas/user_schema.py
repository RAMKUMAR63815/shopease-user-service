from datetime import date, datetime
from typing import Literal

import phonenumbers
from phonenumbers import NumberParseException
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# Only accept these gender values
GenderType = Literal[
    "MALE",
    "FEMALE",
    "OTHER",
    "PREFER_NOT_TO_SAY",
]


# Common settings for incoming API request schemas
class InputSchema(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True, #It automatically removes unnecessary spaces from the beginning and end of string values.
        extra="forbid", #It prevents users from sending fields that are not defined in your schema.
    ) 


# Convert and validate phone numbers
def normalize_phone_number(value: str) -> str:
    try:
        # Use India as the default region for numbers without country code
        region = None if value.startswith("+") else "IN"

        parsed_number = phonenumbers.parse(value, region) #phonenumbers is a Python library used to parse and validate international phone numbers. It converts the input into a structured phone number object.

        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Please provide a valid phone number")

        # Return phone number in international E.164 format
        return phonenumbers.format_number(
            parsed_number,
            phonenumbers.PhoneNumberFormat.E164,
        )

    except NumberParseException as exc:
        raise ValueError("Invalid phone number format") from exc


# Normalize gender values
def normalize_gender(value):
    if value is None:
        return None

    if isinstance(value, str):
        return value.strip().upper()

    return value


# Validate date of birth
def validate_date_of_birth(value):
    if value is not None and value > date.today():
        raise ValueError("Date of birth cannot be in the future")

    return value


# Common profile fields
class UserProfileFields(InputSchema):

    full_name: str = Field(
        min_length=2,
        max_length=150,
    )

    phone_number: str = Field(
        min_length=7,
        max_length=20,
    )

    date_of_birth: date | None = None

    gender: GenderType | None = None

    profile_image: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Full name cannot be empty")

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone_number(value)

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value):
        return validate_date_of_birth(value)

    @field_validator("gender", mode="before")
    @classmethod
    def validate_gender(cls, value):
        return normalize_gender(value)

    @field_validator("profile_image")
    @classmethod
    def validate_profile_image(cls, value):
        if value is not None and not value.strip():
            return None

        return value


# Create profile request
class UserProfileCreate(UserProfileFields):
    pass


# Full profile update request (PUT)
class UserProfileUpdate(UserProfileFields):
    pass


# Partial profile update request (PATCH)
class UserProfilePatch(InputSchema):

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    phone_number: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
    )

    date_of_birth: date | None = None

    gender: GenderType | None = None

    profile_image: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value):
        if value is None or not value.strip():
            raise ValueError("Full name cannot be empty")

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            raise ValueError("Phone number cannot be empty")

        return normalize_phone_number(value)

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value):
        return validate_date_of_birth(value)

    @field_validator("gender", mode="before")
    @classmethod
    def validate_gender(cls, value):
        return normalize_gender(value)

    @field_validator("profile_image")
    @classmethod
    def validate_profile_image(cls, value):
        if value is not None and not value.strip():
            return None

        return value

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")

        return self


# Safe profile response
# Never expose auth credentials or database password fields
class UserProfileResponse(BaseModel):

    id: int
    full_name: str
    phone_number: str

    date_of_birth: date | None = None
    gender: str | None = None
    profile_image: str | None = None

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
