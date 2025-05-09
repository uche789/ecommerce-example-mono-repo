from typing import Annotated, List
from sqlalchemy.orm import Session, aliased
from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile, Request, Response
from contextlib import asynccontextmanager
from dbsetup import DataModel;
from fastapi.staticfiles import StaticFiles
from models import (
    Product, Inventory, Category, CategoryPublic,
    Discount, DiscountNewRequest, Pricing, ProductImage,
    PricingPublic, UpdatePricing, InventoryNewRequest, InventoryUpdateRequest,
    ProductPublic, ProductRequest, CategoryUpdateRequest, ProductUpdateRequest,
    DiscountUpdateRequest, ProductPricingPublic, ProductCategory, ProductDiscountPublic,
    ProductInventoryPublic, RelatedProductImage
)
import os
import shutil
import uuid;
from lib.contraints import is_valid_image, matchesExpression, hasAnyAttributes
import logging
from sqlalchemy import update, exists, and_
import pathlib

# https://github.com/zhanymkanov/fastapi-best-practices

dm = DataModel()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log") # Log to file
    ]
)
logger = logging.getLogger('inventory.logger')

IMAGE_DIR = 'static/images'

@asynccontextmanager
async def lifespan(app: FastAPI):
    dm.create_db_and_tables()
    yield

SessionDep = Annotated[Session, Depends(dm.get_session)]
app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

# PRODUCTS #

@app.get("/products", response_model=List[ProductPublic])
def get_product(session: SessionDep, limit: int = 100, offset: int = 0, category_id: int = None, query = ''):
    AliasedDiscount = aliased(Discount)
    subq = (
        session.query(AliasedDiscount)
        .filter(
            AliasedDiscount.item_id == Product.product_id,
            AliasedDiscount.active == True
        )
        .order_by(AliasedDiscount.discount_id)
        .limit(1)
        .correlate(Product)
        .subquery()
    )

    sqlquery = session.query(Product, Category, Inventory, Pricing, AliasedDiscount)

    if query:
        sqlquery = sqlquery.filter(Product.product_name.ilike(f"%{query}%"))

    if category_id:
        sqlquery = sqlquery.join(Category, and_(
            Category.category_id == category_id,
            Category.category_id == Product.category_id,
        ))
    else:
       sqlquery = sqlquery.outerjoin(Category, Category.category_id == Product.category_id)

    sqlquery = (
        sqlquery
        .outerjoin(Product.inventory)
        .outerjoin(Product.pricing)
    )

    sqlresults =  (
        sqlquery.outerjoin(AliasedDiscount, AliasedDiscount.item_id == Product.product_id)
        .limit(limit)
        .offset(offset)
        .all()
    )

    results: List[ProductPublic] = []

    for row in sqlresults:
        discount = None
        if hasattr(row[4], 'discount_id'):
            discount = ProductDiscountPublic(
                discounted_amount=row[4].amount
            )

        product_pricing = ProductPricingPublic(
            orginal_price= row[3].amount if hasattr(row[3], 'amount') else 0,
            discount=discount
        )

        product_category = None
        if hasattr(row[1], 'category_name'):
            product_category = ProductCategory(
                category_name=row[1].category_name
            )

        product_inventory = ProductInventoryPublic(
            inventory_id=row[2].quantity if hasattr(row[2], 'quantity') else None,
            quantity=row[2].quantity if hasattr(row[2], 'quantity') else 0,
            sku=row[2].sku if hasattr(row[2], 'sku') else None,
            status=row[2].status if hasattr(row[2], 'sku') else 'offline',
        )

        product = ProductPublic(
            product_id=row[0].product_id,
            product_name=row[0].product_name,
            description=row[0].description,
            slug=row[0].slug,
            pricing=product_pricing,
            category=product_category,
            inventory=product_inventory
        )

        results.append(product)

    for product in results:
        images = session.query(ProductImage).filter(ProductImage.product_id == product.product_id).all()
        for image in images:
            product.product_images.append(RelatedProductImage(
                image_url=image.product_image,
                main_image=image.main_image,
            ))
    return results

@app.post("/products")
def add_product(session: SessionDep, payload: ProductRequest):
    db_table = Product(
        product_name = payload.product_name,
        description = payload.description,
        category_id = payload.category_id,
        slug = payload.product_name.lower().strip().replace(' ', '-')
    )
    session.add(db_table)
    session.commit()

@app.patch("/products/{product_id}")
def update_pricing(session: SessionDep, product_id: int, payload: ProductUpdateRequest):
    result = session.get(Product, product_id)

    if not result:
        raise HTTPException(status_code=404, detail="Product pricing not found")
    
    if payload.category_id:
        result.category_id = payload.category_id
    if payload.description:
        result.description = payload.description
    if payload.product_name:
        result.product_name = payload.product_name
        result.slug = payload.product_name.lower().strip().replace(' ', '-')
    session.commit()


# INVENTORY #

@app.post("/products/inventory")
def add_inventory_data(session: SessionDep, payload: InventoryNewRequest):
    product = session.get(Product, payload.product_id)
    if not product:
        raise HTTPException(404, detail="Product is not available")
    
    found = session.query(exists().where(Inventory.product_id == payload.product_id)).scalar()

    if found:
        raise HTTPException(400, detail="Product inventory already exists")

    db_payload = Inventory(
        product_id = payload.product_id,
        sku = payload.sku,
        quantity = payload.quantity,
        status = payload.status
    )
    session.add(db_payload)
    session.commit()

@app.patch("/products/inventory/{inventory_id}")
def add_inventory(session: SessionDep, inventory_id: int, payload: InventoryUpdateRequest):
    result = session.get(Inventory, inventory_id)

    if not payload.quantity and not payload.status:
        raise HTTPException(status_code=400, detail="Quantity or status arguments are required")

    if not result:
        raise HTTPException(status_code=404, detail="Product inventory not found")
    
    if payload.status:
        result.status = payload.status
    
    if payload.quantity:
        result.quantity = payload.quantity

    if payload.sku:
        result.quantity = payload.sku
    
    session.commit()


# PRICING #

@app.post("/pricing")
def add_pricing(session: SessionDep, payload: PricingPublic):
    product = session.get(Product, payload.product_id)
    if not product:
        raise HTTPException(404, detail="Product is not available")
    
    db_payload = Pricing(
        product_id = payload.product_id,
        amount = payload.amount
    )

    session.add(db_payload)
    session.commit()

@app.patch("/pricing/{pricing_id}")
def update_pricing(session: SessionDep, pricing_id: int, payload: UpdatePricing):
    result = session.get(Pricing, pricing_id)

    if not result:
        raise HTTPException(status_code=404, detail="Product pricing not found")
    
    result.amount = payload.amount
    session.commit()

# PRODUCT IMAGE #

@app.get("/products/{product_id}/images")
def set_product_main_image(session: SessionDep, product_id: int):
    result = session.query(ProductImage).filter(ProductImage.product_id == product_id).all()
    return result

@app.post("/products/{product_id}/images/{product_image_id}/main")
def set_product_main_image(session: SessionDep, product_image_id: int, product_id: int):
    result = session.get(ProductImage, product_image_id)

    if not result:
        raise HTTPException(status_code=404, detail="Product image not found")
    
    session.execute(
        update(ProductImage)
        .where(ProductImage.product_id == product_id)
        .values(main_image=False)
    )
    session.commit()

    result.main_image = True
    session.commit()

@app.post("/products/{product_id}/images")
def add_product_images(session: SessionDep, product_id: int, files: list[UploadFile]):
    result = session.get(Product, product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    
    count = session.query(ProductImage).where(ProductImage.product_id == product_id).count()

    if count > 10:
        raise HTTPException(status_code=500, detail="Exceeds 10 images per product")
    
    files_result = {
        "saved": [],
        "skipped": []
    }

    for file in files:
        try: 
            if not is_valid_image(file.content_type):
                logger.error("Invalid mime type")
                continue
            
            new_file_name = uuid.uuid4().__str__() + pathlib.Path(file.filename).suffix
            file_location = os.path.join(IMAGE_DIR, new_file_name)
            with open(file_location, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
                db_payload = ProductImage(
                    product_id = product_id,
                    product_image = file_location,
                )
                session.add(db_payload)
                session.commit()
            files_result["saved"].append(file.filename)
        except Exception as e:
            logger.error("Failed to upload product image", e)
            files_result["skipped"].append(file.filename)
    
    return files_result

@app.delete('/products/{product_id}/images/{product_image_id}')
def delete_product_image(session: SessionDep, product_id: int, product_image_id: int):
    result = session.query(ProductImage).where(
        ProductImage.product_id == product_id,
        ProductImage.product_image_id == product_image_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Product or product image not found")
    
    if result.main_image:
        raise HTTPException(status_code=500, detail="Cannot delete main image")

    try:
        if os.path.exists(result.product_image):
            os.remove(result.product_image)
            session.delete(result)
            session.commit()
            return Response(status_code=200)
    except Exception as e:
        logger.error("Failed to delete product image", e)
        raise HTTPException(status_code=500, detail='Failed to delete product image')

    return Response(status_code=204)

# CATEGORIES #

@app.get('/categories')
def get_categories(session: SessionDep):
    result = session.query(Category).all()
    return result

@app.get('/categories/{category_id}')
def get_categories(session: SessionDep, category_id: int):
    result = session.get(Category, category_id)
    # TODO: Add breadcrumbs
    return result

@app.post('/categories')
def add_category(session: SessionDep, payload: CategoryUpdateRequest):
    db_payload = Category(
        category_name = payload.category_name,
        slug = payload.slug,
        parent = payload.parent,
        description = payload.description,
        category_key = payload.category_key,
    )
    session.add(db_payload)
    session.commit()

@app.patch('/categories/{category_id}')
def update_category(session: SessionDep, payload: CategoryUpdateRequest, category_id: int):
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404)
    if payload.description:
        db_category.description = payload.description
    if hasattr(payload, 'parent'):
        db_category.parent = payload.parent
    if payload.category_name:
        db_category.category_name = payload.category_name
    if payload.slug:
        db_category.slug = payload.slug
    if payload.category_key:
        db_category.category_key = payload.category_key
    session.commit()

@app.post("/categories/{category_id}/image")
def add_category_image(session: SessionDep, category_id: int, file: UploadFile) -> str:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Product not found")

    oldImageUrl = category.image_url
    new_file_name = uuid.uuid4().__str__() + pathlib.Path(file.filename).suffix
    file_location = os.path.join(IMAGE_DIR, new_file_name)

    try: 
        if not is_valid_image(file.content_type):
            logger.error("Invalid mime type")
            raise HTTPException(status_code=400, detail="Invalid Mime Type")
        
        with open(file_location, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
            category.image_url = file_location
            session.commit()
    except Exception as e:
        logger.error("Failed to upload product image", e)
        raise HTTPException(status_code=500)
    
    # delete old category image
    try:
        if (oldImageUrl and os.path.exists(oldImageUrl)):
            os.remove(oldImageUrl)
    except Exception as e:
        logger.error("Failed to delete old category image", {
            "category_id": category_id,
            "category_image": oldImageUrl
        })

    return file_location

# DISCOUNTS # 

@app.post('/discounts')
def add_discount(session: SessionDep, payload: DiscountNewRequest):
    hasActiveDiscount = (
            session.query(Discount)
            .where(
                Discount.item_id == payload.item_id,
                Discount.item_type == payload.discount_type,
                Discount.active == True
            )
        )
    
    if hasActiveDiscount:
        raise HTTPException("An active discount already exisits for the item")

    if payload.discount_type in ["amount", "percent"]:
        raise HTTPException("Invalid argument: discount_type")
    
    if payload.item_type in ["product", "category"]:
        raise HTTPException("Invalid argument: item_type")


    db_payload = Discount(
        amount = payload.amount,
        item_type = payload.item_type,
        discount_type = payload.discount_type,
        item_id = payload.item_id,
        expires_on = payload.expires_on,
        starts_on = payload.starts_on,
    )
    session.add(db_payload)
    session.commit()

@app.patch('/discounts/{discount_id}')
def add_discount(session: SessionDep, discount_id: int, payload: DiscountUpdateRequest):
    discount = session.get(Discount,discount_id)
    if not discount:
        raise HTTPException(404, detail="Item discount not found")
    
    if hasAnyAttributes(payload) == False:
        return
    
    if payload.active != None:
        discount.active = payload.active
    if payload.amount:
        discount.amount = payload.amount
    if payload.expires_on:
        discount.expires_on = payload.expires_on
    if payload.starts_on:
        discount.starts_on = payload.starts_on
    session.commit()
