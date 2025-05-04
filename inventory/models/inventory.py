from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, create_engine, JSON, CheckConstraint, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, sessionmaker
from pydantic import BaseModel
from models.base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id = mapped_column(ForeignKey("product.product_id"))
    quantity: Mapped[float]
    status: Mapped[str] = mapped_column(String(10))
    # execute lamba function each time a new record is added
    date_updated = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('offline', 'online')",
            name="status_constraint"
        ),
    )

class InventoryPublic(BaseModel):
    product_id: int
    quantity: int
    status: str = 'offline'

class UpdateInventory(BaseModel):
    quantity: int | None
    status: str | None
