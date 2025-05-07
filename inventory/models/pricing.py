from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base

class Pricing(Base):
    __tablename__ = "pricing"

    pricing_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id = mapped_column(ForeignKey("product.product_id"), unique=True)
    amount: Mapped[float]
    
    product = relationship("Product", back_populates="pricing")

class PricingPublic(BaseModel):
    product_id: int
    amount: float
class UpdatePricing(BaseModel):
    amount: float