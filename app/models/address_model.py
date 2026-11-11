from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class UserAddress(Base):

    # MySQL table name
    __tablename__ = "user_addresses"

    # Index helps retrieve addresses belonging to a user
    __table_args__ = (
        Index(
            "ix_user_addresses_user_id",
            "user_id",
        ),
    )

    # Address primary key
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Foreign key to the local user_profiles table
    user_id = Column(
        Integer,
        ForeignKey(
            "user_profiles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # Address category: HOME, OFFICE or OTHER
    address_type = Column(
        String(20),
        nullable=False,
    )

    # Person receiving the delivery
    full_name = Column(
        String(150),
        nullable=False,
    )

    # Recipient contact number
    phone_number = Column(
        String(20),
        nullable=False,
    )

    # Main address
    address_line_1 = Column(
        String(255),
        nullable=False,
    )

    # Additional address information
    address_line_2 = Column(
        String(255),
        nullable=True,
    )

    # City
    city = Column(
        String(100),
        nullable=False,
    )

    # State
    state = Column(
        String(100),
        nullable=False,
    )

    # Country
    country = Column(
        String(100),
        nullable=False,
    )

    # Postal or ZIP code
    postal_code = Column(
        String(20),
        nullable=False,
    )

    # Indicates whether this is the user's default address
    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
    )

    # Address creation timestamp
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    # Connect this address back to its profile
    user = relationship(
        "UserProfile",
        back_populates="addresses",
    )

    def __repr__(self):
        return (
            f"UserAddress(id={self.id}, "
            f"user_id={self.user_id}, "
            f"address_type={self.address_type!r}, "
            f"city={self.city!r}, "
            f"is_default={self.is_default})"
        )
