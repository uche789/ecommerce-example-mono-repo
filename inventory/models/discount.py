from sqlalchemy import CheckConstraint, Integer, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base

class Discount(Base):
    __tablename__ = "discount"

    discount_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int]
    discount_type: Mapped[str]
    item_type: Mapped[str]
    amount: Mapped[float]
    starts_on = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_on = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint(
            "discount_type IN ('amount', 'percent')",
            name="discount_type_constraint"
        ),
        CheckConstraint(
            "item_type IN ('category', 'product')",
            name="item_type_constraint"
        ),
    )

class DiscountPublic(BaseModel):
    discount_id: int | None
    item_id: int
    discount_type: str
    item_type: str
    amount: float
    starts_on: str
    expires_on: str
