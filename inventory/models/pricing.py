from sqlalchemy import ForeignKey, create_engine, JSON, CheckConstraint, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, sessionmaker
from pydantic import BaseModel
from models.base import Base

class Pricing(Base):
    __tablename__ = "pricing"

    pricing_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id = mapped_column(ForeignKey("product.product_id"))
    amount: Mapped[float]
