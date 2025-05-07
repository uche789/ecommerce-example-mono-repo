from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column, relationship
from pydantic import BaseModel
from models.base import Base

class Product(Base):
    __tablename__ = "product"

    product_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name = mapped_column(String(250), unique=True)
    description = mapped_column(String(500))
    category_id = mapped_column(Integer, nullable=True)

    inventory = relationship("Inventory", uselist=False, back_populates="product")
    pricing = relationship("Pricing", uselist=False, back_populates="product")

    # category = relationship("Category", backref="products")
    # inventory_item = relationship("Inventory")
    # pricing = relationship("Pricing") 

class ProductPublic(BaseModel):
    product_id: int
    product_name: str
    description: str
    category_id: int | None

    class Config:
        orm_mode = True

class ProductRequest(BaseModel):
    product_name: str
    description: str
    category_id: int | None
