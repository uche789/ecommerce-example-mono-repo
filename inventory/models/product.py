from sqlalchemy import create_engine, JSON, CheckConstraint, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, sessionmaker
from pydantic import BaseModel
from models.base import Base

class Product(Base):
    __tablename__ = "product"

    product_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name = mapped_column(String(250), unique=True)
    product_sku = mapped_column(String(250), index=True, unique=True)
    description = mapped_column(String(500))
    category_id = mapped_column(Integer, default=0)

class ProductPublic(BaseModel):
    product_name: str
    product_sku: str
    description: str
    category_id: int 
