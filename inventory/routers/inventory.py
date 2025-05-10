from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from models import (
    Product, Inventory
)
from sqlalchemy import exists
from lib import DataModel
from models.inventory import InventoryNewRequest, InventoryUpdateRequest


router = APIRouter()
dm = DataModel()
SessionDep = Annotated[Session, Depends(dm.get_session)]

@router.post("/products/inventory")
def add_inventory_data(session: SessionDep, payload: InventoryNewRequest):
    product = session.get(Product, payload.product_id)
    if not product:
        raise HTTPException(404, detail="Product is not available")
    
    found = session.query(exists().where(Inventory.product_id == payload.product_id)).scalar()

    if found:
        raise HTTPException(400, detail="Product inventory already exists")

    db_payload = Inventory(
        product_id = payload.product_id,
        sku = payload.sku,
        quantity = payload.quantity,
        status = payload.status
    )
    session.add(db_payload)
    session.commit()

@router.patch("/products/inventory/{inventory_id}")
def add_inventory(session: SessionDep, inventory_id: int, payload: InventoryUpdateRequest):
    result = session.get(Inventory, inventory_id)

    if not payload.quantity and not payload.status:
        raise HTTPException(status_code=400, detail="Quantity or status arguments are required")

    if not result:
        raise HTTPException(status_code=404, detail="Product inventory not found")
    
    if payload.status:
        result.status = payload.status
    
    if payload.quantity:
        result.quantity = payload.quantity

    if payload.sku:
        result.quantity = payload.sku
    
    session.commit()