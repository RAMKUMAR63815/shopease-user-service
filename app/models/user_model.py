from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class UserProfile(Base):

    # MySQL table name
    __tablename__ = "user_profiles"

    # Each Authentication Service user can have only one profile
    __table_args__ = (
        UniqueConstraint(
            "auth_user_id",
            name="uq_user_profiles_auth_user_id",
        ),
    )

    # Local profile primary key
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # User ID received from the Authentication Service
    # This is not a foreign key to another service's database
    auth_user_id = Column(
        Integer,
        nullable=False,
    )

    # Customer full name
    full_name = Column(
        String(150),
        nullable=False,
    )

    # Customer contact number
    phone_number = Column(
        String(20),
        nullable=False,
    )

    # Optional date of birth
    date_of_birth = Column(
        Date,
        nullable=True,
    )

    # Optional gender information
    gender = Column(
        String(20),
        nullable=True,
    )

    # Optional profile image URL or path
    profile_image = Column(
        String(500),
        nullable=True,
    )

    # Local profile activation status
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    # Profile creation timestamp
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    # Profile update timestamp
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # One profile can have multiple addresses
    addresses = relationship(
        "UserAddress",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return (
            f"UserProfile(id={self.id}, "
            f"auth_user_id={self.auth_user_id}, "
            f"full_name={self.full_name!r}, "
            f"phone_number={self.phone_number!r}, "
            f"is_active={self.is_active})"
        )
