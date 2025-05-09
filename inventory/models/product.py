from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column, relationship, Mapped
from pydantic import BaseModel
from models.base import Base
from typing import Optional

class Product(Base):
    __tablename__ = "product"

    product_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name = mapped_column(String(250), unique=True)
    description = mapped_column(String(500))
    category_id = mapped_column(Integer, nullable=True)
    slug = mapped_column(Integer, nullable=True)

    inventory = relationship("Inventory", uselist=False, back_populates="product")
    pricing = relationship("Pricing", uselist=False, back_populates="product")

class ProductInventoryPublic(BaseModel):
    inventory_id: int
    sku: str
    quantity: int
    status: str = 'offline'

class ProductDiscountPublic(BaseModel):
    discounted_amount: float
    starts_on: str
    expires_on: str
    active: bool

class ProductPricingPublic(BaseModel):
    orginal_price: float
    discount: Optional[ProductDiscountPublic]

class ProductPublic(BaseModel):
    product_id: int
    product_name: str
    description: str
    category_id: int | None
    slug: str
    inventory: Optional[ProductInventoryPublic]
    pricing: ProductPricingPublic

    class Config:
        from_attributes = True

class ProductRequest(BaseModel):
    product_name: str
    description: str
    category_id: int | None
    slug: str

class ProductUpdateRequest(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None