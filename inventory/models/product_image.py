from sqlalchemy import Boolean, ForeignKey, create_engine, JSON, CheckConstraint, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, sessionmaker
from pydantic import BaseModel
from models.base import Base

class ProductImage(Base):
    __tablename__ = "product_image"

    price_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id = mapped_column(ForeignKey("product.product_id"))
    product_image: Mapped[str]
    sort_order = mapped_column(Integer, default=1)
    is_delete: Mapped[bool] = mapped_column(Boolean, default=False)

class ProductImagePublic(BaseModel):
    product_id: int
    product_image: str
    sort_order: int