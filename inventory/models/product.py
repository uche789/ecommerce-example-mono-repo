from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column, relationship, Mapped
from pydantic import BaseModel
from models.base import Base
from typing import Optional, List

class Product(Base):
    __tablename__ = "product"

    product_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name = mapped_column(String(250), unique=True)
    description = mapped_column(String(500))
    category_id: Mapped[int] = mapped_column(Integer, nullable=True)
    slug = mapped_column(Integer, nullable=True)

    inventory = relationship("Inventory", uselist=False, back_populates="product")
    pricing = relationship("Pricing", uselist=False, back_populates="product")

class ProductInventoryPublic(BaseModel):
    inventory_id: int | None
    sku: str | None
    quantity: int
    status: str = 'offline'

class ProductDiscountPublic(BaseModel):
    discounted_amount: float
    discount_type: str

class ProductCategory(BaseModel):
    category_name: str

class ProductPricingPublic(BaseModel):
    orginal_price: float
    discount: Optional[ProductDiscountPublic]

class RelatedProductImage(BaseModel):
    image_url: str
    main_image: bool

class ProductPublic(BaseModel):
    product_id: int
    product_name: str
    description: str | None
    category: ProductCategory | None
    slug: str
    inventory: Optional[ProductInventoryPublic]
    pricing: ProductPricingPublic
    product_images: List[RelatedProductImage] = []

    class Config:
        from_attributes = True

class ProductRequest(BaseModel):
    product_name: str
    description: Optional[str] = None
    category_id: int | None
    slug: str

class ProductUpdateRequest(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None