from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import and_, asc, desc
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import AvailabilityOffer, AvailabilityRequest, Notification, User
from .users import get_current_user
from ..services.email import send_email


router = APIRouter()


class SlotIn(BaseModel):
    start_at: datetime
    end_at: datetime

    @property
    def valid(self) -> bool:
        return self.end_at > self.start_at


def _notify(db: Session, user: User, message: str) -> None:
    notif = Notification(user_id=user.id, message=message)
    db.add(notif)
    send_email(user.email, "Miguafi - Nouvelle correspondance", message)


def _match_offer(db: Session, offer: AvailabilityOffer) -> None:
    # Find requests that fit within offer window
    matches = (
        db.query(AvailabilityRequest)
        .filter(
            and_(
                AvailabilityRequest.start_at >= offer.start_at,
                AvailabilityRequest.end_at <= offer.end_at,
                AvailabilityRequest.user_id != offer.user_id,
            )
        )
        .all()
    )
    for req in matches:
        if req.user:  # Notify requester about offer
            _notify(db, req.user, f"Une offre correspond à votre demande du {req.start_at} au {req.end_at}.")


def _match_request(db: Session, request: AvailabilityRequest) -> None:
    # Find offers that contain the requested window
    matches = (
        db.query(AvailabilityOffer)
        .filter(
            and_(
                AvailabilityOffer.start_at <= request.start_at,
                AvailabilityOffer.end_at >= request.end_at,
                AvailabilityOffer.user_id != request.user_id,
            )
        )
        .all()
    )
    for off in matches:
        if off.user:  # Notify offer owner about request
            _notify(db, off.user, f"Une demande correspond à votre offre du {off.start_at} au {off.end_at}.")


@router.post("/offers", response_model=dict)
def create_offer(slot: SlotIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not slot.valid:
        raise HTTPException(status_code=400, detail="Invalid time range")
    # Prevent past and overlapping windows
    now = datetime.utcnow()
    if slot.end_at <= now or slot.start_at <= now:
        raise HTTPException(status_code=400, detail="Time range must be in the future")
    overlap = (
        db.query(AvailabilityOffer)
        .filter(
            AvailabilityOffer.user_id == current_user.id,
            # overlap if start < existing.end and end > existing.start
            AvailabilityOffer.start_at < slot.end_at,
            AvailabilityOffer.end_at > slot.start_at,
        )
        .first()
    )
    if overlap:
        raise HTTPException(status_code=400, detail="Overlapping offer exists")
    offer = AvailabilityOffer(user_id=current_user.id, start_at=slot.start_at, end_at=slot.end_at)
    db.add(offer)
    db.commit()
    db.refresh(offer)
    _match_offer(db, offer)
    db.commit()
    return {"id": offer.id}


@router.post("/requests", response_model=dict)
def create_request(slot: SlotIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not slot.valid:
        raise HTTPException(status_code=400, detail="Invalid time range")
    # Prevent past and overlapping windows
    now = datetime.utcnow()
    if slot.end_at <= now or slot.start_at <= now:
        raise HTTPException(status_code=400, detail="Time range must be in the future")
    overlap = (
        db.query(AvailabilityRequest)
        .filter(
            AvailabilityRequest.user_id == current_user.id,
            AvailabilityRequest.start_at < slot.end_at,
            AvailabilityRequest.end_at > slot.start_at,
        )
        .first()
    )
    if overlap:
        raise HTTPException(status_code=400, detail="Overlapping request exists")
    req = AvailabilityRequest(user_id=current_user.id, start_at=slot.start_at, end_at=slot.end_at)
    db.add(req)
    db.commit()
    db.refresh(req)
    _match_request(db, req)
    db.commit()
    return {"id": req.id}


@router.delete("/offers/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer(offer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = db.get(AvailabilityOffer, offer_id)
    if not obj or obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Offer not found")
    db.delete(obj)
    db.commit()
    return


@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = db.get(AvailabilityRequest, request_id)
    if not obj or obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    db.delete(obj)
    db.commit()
    return


@router.get("/offers/mine", response_model=dict)
def my_offers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = 1,
    page_size: int = 20,
    sort: str = "-start_at",  # - for desc
):
    q = db.query(AvailabilityOffer).filter(AvailabilityOffer.user_id == current_user.id)
    total = q.count()
    order_col = AvailabilityOffer.start_at
    order = desc(order_col) if sort.startswith('-') else asc(order_col)
    items = (
        q.order_by(order)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [{"id": r.id, "start_at": r.start_at.isoformat(), "end_at": r.end_at.isoformat()} for r in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/requests/mine", response_model=dict)
def my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = 1,
    page_size: int = 20,
    sort: str = "-start_at",
):
    q = db.query(AvailabilityRequest).filter(AvailabilityRequest.user_id == current_user.id)
    total = q.count()
    order_col = AvailabilityRequest.start_at
    order = desc(order_col) if sort.startswith('-') else asc(order_col)
    items = (
        q.order_by(order)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [{"id": r.id, "start_at": r.start_at.isoformat(), "end_at": r.end_at.isoformat()} for r in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
