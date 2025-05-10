from typing import Annotated, List
from sqlalchemy.orm import Session, aliased
from fastapi import Depends, FastAPI, HTTPException, Response, UploadFile, Response
from contextlib import asynccontextmanager
from dbsetup import DataModel
from fastapi.staticfiles import StaticFiles
from models import (
    Product, Inventory, Category,
    Discount, DiscountNewRequest, Pricing, ProductImage,
    PricingPublic, UpdatePricing, InventoryNewRequest, InventoryUpdateRequest,
    ProductPublic, ProductRequest, CategoryUpdateRequest, ProductUpdateRequest,
    DiscountUpdateRequest, ProductPricingPublic, ProductCategory, ProductDiscountPublic,
    ProductInventoryPublic, RelatedProductImage
)
import os
import shutil
import uuid;
from lib import is_valid_image, hasAnyAttributes, get_logger, validate_api_key
import logging
from sqlalchemy import update, exists, and_
import pathlib
from datetime import datetime, timezone
from dateutil import parser
from dotenv import load_dotenv
import routers

load_dotenv()

# https://github.com/zhanymkanov/fastapi-best-practices
# https://fastapi.tiangolo.com/tutorial/bigger-applications/#import-the-apirouter

dm = DataModel()

@asynccontextmanager
async def lifespan(app: FastAPI):
    dm.create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    dependencies=[Depends(validate_api_key)]
)
app.include_router(routers.categories.router)
app.include_router(routers.discounts.router)
app.include_router(routers.inventory.router)
app.include_router(routers.pricing.router)
app.include_router(routers.product_images.router)
app.include_router(routers.products.router)
app.mount("/static", StaticFiles(directory="static"), name="static")
