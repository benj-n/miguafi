from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import os
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..db import get_db
from ..models import Dog, UserDog, User
from ..schemas import DogCreate, DogUpdate, DogOut
from .users import get_current_user
from ..services import storage as storage_mod

router = APIRouter()


def _ensure_owner(db: Session, user_id: str, dog_id: int) -> Dog:
    dog = db.get(Dog, dog_id)
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    link = (
        db.query(UserDog)
        .filter(and_(UserDog.user_id == user_id, UserDog.dog_id == dog_id, UserDog.is_owner.is_(True)))
        .first()
    )
    if not link:
        raise HTTPException(status_code=403, detail="Not an owner")
    return dog


@router.get("/me", response_model=list[DogOut])
def list_my_dogs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(Dog)
        .join(UserDog, UserDog.dog_id == Dog.id)
        .filter(UserDog.user_id == current_user.id)
        .order_by(Dog.created_at.desc())
        .all()
    )
    return rows


@router.post("/", response_model=DogOut)
def create_dog(payload: DogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dog = Dog(name=payload.name, photo_url=payload.photo_url)
    db.add(dog)
    db.flush()  # get id
    db.add(UserDog(user_id=current_user.id, dog_id=dog.id, is_owner=True))
    db.commit()
    db.refresh(dog)
    return dog


@router.put("/{dog_id}", response_model=DogOut)
def update_dog(dog_id: int, payload: DogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dog = _ensure_owner(db, current_user.id, dog_id)
    # Enforce name immutability
    if getattr(payload, "name", None) is not None:
        raise HTTPException(status_code=400, detail="Dog name is immutable")
    if payload.photo_url is not None:
        dog.photo_url = payload.photo_url
    db.add(dog)
    db.commit()
    db.refresh(dog)
    return dog


@router.delete("/{dog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dog(dog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dog = _ensure_owner(db, current_user.id, dog_id)
    # Cascade via relationships will remove links
    db.delete(dog)
    db.commit()
    return


@router.post("/{dog_id}/photo", response_model=DogOut)
def upload_dog_photo(
    dog_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dog = _ensure_owner(db, current_user.id, dog_id)
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")
    try:
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
    except Exception:
        size = 0
    if size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    storage = storage_mod.get_storage()
    # Save with original filename to preserve extension if present
    filename = file.filename or "upload"
    url = storage.save(file.file, filename, content_type=file.content_type)
    dog.photo_url = url
    db.add(dog)
    db.commit()
    db.refresh(dog)
    return dog


@router.post("/{dog_id}/coowners/{user_id}", status_code=200)
def add_coowner(dog_id: int, user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ = _ensure_owner(db, current_user.id, dog_id)
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    existing = db.query(UserDog).filter(and_(UserDog.user_id == user_id, UserDog.dog_id == dog_id)).first()
    if existing:
        existing.is_owner = True
        db.add(existing)
    else:
        db.add(UserDog(user_id=user_id, dog_id=dog_id, is_owner=True))
    db.commit()
    return {"status": "ok"}


@router.delete("/{dog_id}/coowners/{user_id}", status_code=200)
def remove_coowner(dog_id: int, user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ = _ensure_owner(db, current_user.id, dog_id)
    link = db.query(UserDog).filter(and_(UserDog.user_id == user_id, UserDog.dog_id == dog_id)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(link)
    db.commit()
    return {"status": "ok"}
