from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column, relationship
from pydantic import BaseModel
from models.base import Base

class Category(Base):
    __tablename__ = "category"

    category_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_name = mapped_column(String(250), nullable=False, unique=True)
    description = mapped_column(String(500), nullable=True)
    parent = mapped_column(Integer, nullable=True)
    image_url = mapped_column(String, nullable=True)
    slug = mapped_column(String(250), index=True, unique=True)

class CategoryPublic(BaseModel):
    description: str
    category_name: str
    parent: int | None

class CategoryPublic(BaseModel):
    description: str
    category_name: str
    parent: int | None
