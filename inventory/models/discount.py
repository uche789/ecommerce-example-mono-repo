from sqlalchemy import Boolean, CheckConstraint, Integer, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from models.base import Base

class Discount(Base):
    __tablename__ = "discount"

    discount_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_ids: Mapped[str]
    discount_type: Mapped[str]
    item_type: Mapped[str]
    amount: Mapped[float]
    starts_on = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_on = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    active: Mapped[bool] = mapped_column(Boolean, default=False)

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
    discount_id: int
    item_ids: int
    discount_type: str
    item_type: str
    amount: float
    starts_on: str
    expires_on: str
    active: bool

class DiscountNewRequest(BaseModel):
    item_ids: str | None
    discount_type: str | None
    item_type: str | None
    amount: float | None
    starts_on: str | None
    expires_on: str | None
    active: bool | None
