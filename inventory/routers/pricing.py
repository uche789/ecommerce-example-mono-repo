from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from models import (
    Product
)
from lib import DataModel
from models.pricing import Pricing, PricingPublic, UpdatePricing


router = APIRouter()
dm = DataModel()
SessionDep = Annotated[Session, Depends(dm.get_session)]

@router.post("/pricing")
def add_pricing(session: SessionDep, payload: PricingPublic):
    product = session.get(Product, payload.product_id)
    if not product:
        raise HTTPException(404, detail="Product is not available")
    
    db_payload = Pricing(
        product_id = payload.product_id,
        amount = payload.amount
    )

    session.add(db_payload)
    session.commit()

@router.patch("/pricing/{pricing_id}")
def update_pricing(session: SessionDep, pricing_id: int, payload: UpdatePricing):
    result = session.get(Pricing, pricing_id)

    if not result:
        raise HTTPException(status_code=404, detail="Product pricing not found")
    
    result.amount = payload.amount
    session.commit()