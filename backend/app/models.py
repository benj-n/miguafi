import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Integer, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .db import Base


def generate_user_id() -> str:
    # Produce an 8-digit numeric ID derived from a UUID
    return str(uuid.uuid4().int % 10**8).zfill(8)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(8), primary_key=True, default=generate_user_id)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Profile fields (dogs moved to separate table with ownership links)
    # Approximate location (low-precision GPS as text for now)
    location_lat: Mapped[float | None] = mapped_column(nullable=True)
    location_lng: Mapped[float | None] = mapped_column(nullable=True)

    # Relationships
    offers: Mapped[list["AvailabilityOffer"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    requests: Mapped[list["AvailabilityRequest"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    # Dogs association links
    dog_links: Mapped[list["UserDog"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class AvailabilityOffer(Base):
    __tablename__ = "availability_offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="offers")


class AvailabilityRequest(Base):
    __tablename__ = "availability_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="requests")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="notifications")


class Dog(Base):
    __tablename__ = "dogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_links: Mapped[list["UserDog"]] = relationship(back_populates="dog", cascade="all, delete-orphan")


class UserDog(Base):
    __tablename__ = "user_dogs"
    __table_args__ = (
        UniqueConstraint('user_id', 'dog_id', name='uq_user_dog'),
        Index('ix_user_dogs_user_id', 'user_id'),
        Index('ix_user_dogs_dog_id', 'dog_id'),
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    dog_id: Mapped[int] = mapped_column(ForeignKey("dogs.id"), primary_key=True)
    is_owner: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="dog_links")
    dog: Mapped[Dog] = relationship(back_populates="user_links")
