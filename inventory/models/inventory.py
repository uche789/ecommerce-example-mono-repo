from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, create_engine, JSON, CheckConstraint, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from models.base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.product_id"), unique=True)
    sku: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(10))
    # execute lamba function each time a new record is added
    date_updated = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    product = relationship("Product", back_populates="inventory")
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('offline', 'online')",
            name="status_constraint"
        ),
    )

class InventoryNewRequest(BaseModel):
    product_id: int
    sku: str
    quantity: int
    status: str = 'offline'

class InventoryUpdateRequest(BaseModel):
    quantity: int | None
    sku: str | None
    status: str | None
