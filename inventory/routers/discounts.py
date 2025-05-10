from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from dbsetup import DataModel
from models import (
    Discount, DiscountNewRequest, DiscountUpdateRequest
)
from lib import hasAnyAttributes
from datetime import timezone
from dateutil import parser
from lib import get_logger

router = APIRouter()
dm = DataModel()
SessionDep = Annotated[Session, Depends(dm.get_session)]
logger = get_logger()

@router.get('/discounts/{item_category}/{item_id}')
def add_discount(session: SessionDep, item_category: str, item_id: int):
    if not item_category in ["product", "category"]:
        raise HTTPException(status_code=400, detail="Invalid argument: item_type")
    
    results = (
            session.query(Discount)
            .where(
                Discount.item_id == item_id,
                Discount.item_type == item_category,
            ).all()
        )
    return results


@router.post('/discounts')
def add_discount(session: SessionDep, payload: DiscountNewRequest):
    hasActiveDiscount = (
            session.query(Discount)
            .where(
                Discount.item_id == payload.item_id,
                Discount.item_type == payload.discount_type,
                Discount.active == True
            ).first()
        )
    
    if hasActiveDiscount:
        raise HTTPException(status_code=500, detail="An active discount already exisits for the item")

    if not payload.discount_type in ["amount", "percent"]:
        raise HTTPException(status_code=400, detail="Invalid argument: discount_type")
    
    if not payload.item_type in ["product", "category"]:
        raise HTTPException(status_code=400, detail="Invalid argument: item_type")

    if payload.amount < 1:
        raise HTTPException(status_code=400, detail="Invalid argument: amount should be greater than 0")

    try:
        db_payload = Discount(
            amount = payload.amount,
            item_type = payload.item_type,
            discount_type = payload.discount_type,
            item_id = payload.item_id,
            expires_on = parser.parse(payload.expires_on).astimezone(timezone.utc),
            starts_on = parser.parse(payload.starts_on).astimezone(timezone.utc),
        )
        session.add(db_payload)
        session.commit()
    except Exception as e:
        logger.error(f"Cannot create discount object: {e}")
        raise HTTPException(status_code=400, detail="Invalid arguments")

@router.patch('/discounts/{discount_id}')
def update_discount(session: SessionDep, discount_id: int, payload: DiscountUpdateRequest):
    discount = session.get(Discount,discount_id)
    if not discount:
        raise HTTPException(404, detail="Item discount not found")

    if hasAnyAttributes(payload) == False:
        return
    
    try:
        if payload.active != None:
            discount.active = payload.active
        if payload.discount_type and payload.amount:
            if not payload.discount_type in ["amount", "percent"]:
                raise HTTPException(status_code=400, detail="Invalid argument: discount_type")
            if payload.amount < 1:
                raise HTTPException(status_code=400, detail="Invalid argument: amount should be greater than 0")
            discount.discount_type = payload.discount_type
            discount.amount = payload.amount
        if payload.expires_on:
            discount.expires_on = parser.parse(payload.expires_on).astimezone(timezone.utc)
        if payload.starts_on:
            discount.starts_on = parser.parse(payload.starts_on).astimezone(timezone.utc)
        session.commit()
    except Exception as e:
        raise HTTPException(500, detail="Failed to update due server error or invalid arguments")