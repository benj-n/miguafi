from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
import os
import re
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User, Dog, UserDog
from ..schemas import Token, UserCreate, UserOut
from ..security import hash_password, verify_password, create_access_token
from ..services import storage as storage_mod
from ..services.email import send_email


router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        location_lat=user_in.location_lat,
        location_lng=user_in.location_lng,
    )
    db.add(user)
    db.flush()  # get user id

    # Optional: create a Dog linked to the user if dog_name provided
    if user_in.dog_name:
        name = user_in.dog_name.upper()
        dog = Dog(name=name)
        db.add(dog)
        db.flush()
        db.add(UserDog(user_id=user.id, dog_id=dog.id, is_owner=True))

    db.commit()
    db.refresh(user)
    # Welcome email (simple bilingual)
    send_email(user.email, "Bienvenue / Welcome to Miguafi", "Bienvenue chez Miguafi!\nWelcome to Miguafi!")
    return user


@router.post("/register-multipart", response_model=UserOut)
def register_multipart(
    email: str = Form(...),
    password: str = Form(...),
    dog_name: str | None = Form(default=None),
    location_lat: float | None = Form(default=None),
    location_lng: float | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=email,
        password_hash=hash_password(password),
        location_lat=location_lat,
        location_lng=location_lng,
    )
    db.add(user)
    db.flush()

    photo_url: str | None = None
    if file is not None:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image uploads are allowed")
        # Enforce max size 10MB
        try:
            file.file.seek(0, os.SEEK_END)
            size = file.file.tell()
            file.file.seek(0)
        except Exception:
            size = 0
        if size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        storage = storage_mod.get_storage()
        filename = file.filename or "upload"
        photo_url = storage.save(file.file, filename, content_type=file.content_type)

    if dog_name:
        name = dog_name.upper()
        # Validate pattern: uppercase letters/digits ending with two digits
        if not re.fullmatch(r"^[A-Z0-9]{1,98}[0-9]{2}$", name):
            raise HTTPException(status_code=400, detail="Invalid dog name format")
        dog = Dog(name=name, photo_url=photo_url)
        db.add(dog)
        db.flush()
        db.add(UserDog(user_id=user.id, dog_id=dog.id, is_owner=True))

    db.commit()
    db.refresh(user)
    send_email(user.email, "Bienvenue / Welcome to Miguafi", "Bienvenue chez Miguafi!\nWelcome to Miguafi!")
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)
