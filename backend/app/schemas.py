from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: EmailStr
    dog_name: Optional[str] = None
    dog_photo_url: Optional[str] = None
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lng: Optional[float] = Field(None, ge=-180, le=180)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    dog_name: Optional[str] = None
    dog_photo_url: Optional[str] = None
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lng: Optional[float] = Field(None, ge=-180, le=180)


class UserOut(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Dogs
class DogBase(BaseModel):
    name: str = Field(min_length=3, max_length=100, pattern=r"^[A-Z0-9]{1,98}[0-9]{2}$")
    photo_url: Optional[str] = None


class DogCreate(DogBase):
    pass


class DogUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100, pattern=r"^[A-Z0-9]{1,98}[0-9]{2}$")
    photo_url: Optional[str] = None


class DogOut(DogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
