from typing import Annotated, List
from sqlalchemy.orm import Session, aliased
from fastapi import Depends, HTTPException, APIRouter
from models import (
    Product, Inventory, Category,
    Discount, Pricing, ProductImage,
    ProductPublic, ProductRequest, ProductUpdateRequest,
    ProductPricingPublic, ProductCategory, ProductDiscountPublic,
    ProductInventoryPublic, RelatedProductImage
)
from sqlalchemy import and_
from datetime import datetime, timezone
from dateutil import parser
from lib import DataModel


router = APIRouter()
dm = DataModel()
SessionDep = Annotated[Session, Depends(dm.get_session)]

@router.get("/products", response_model=List[ProductPublic])
def get_products(session: SessionDep, limit: int = 100, offset: int = 0, category_id: int = None, query = ''):
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
            now = datetime.now(timezone.utc)
            starts_on = parser.parse(row[4].starts_on.strftime("%Y-%m-%d %H:%M:%S")).astimezone(timezone.utc)
            expires_on = parser.parse(row[4].expires_on.strftime("%Y-%m-%d %H:%M:%S")).astimezone(timezone.utc)
            isValidDate = starts_on <= now and expires_on > now
            isValid = bool(row[4].active) == True and isValidDate
            if isValid:
                discount = ProductDiscountPublic(
                    discounted_amount=row[4].amount,
                    discount_type=row[4].discount_type,
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

@router.get("/products/{product_id}", response_model=ProductPublic|None)
def get_product(session: SessionDep, product_id: int):
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

    sqlresult = (
        session.query(Product, Category, Inventory, Pricing, AliasedDiscount)
        .filter(Product.product_id == product_id)
        .outerjoin(Category, Category.category_id == Product.category_id)
        .outerjoin(Product.inventory)
        .outerjoin(Product.pricing)
        .outerjoin(AliasedDiscount, AliasedDiscount.item_id == Product.product_id)
        .first()
    )

    if not sqlresult:
        return

    discount = None
    if hasattr(sqlresult[4], 'discount_id'):
        now = datetime.now(timezone.utc)
        starts_on = parser.parse(sqlresult[4].starts_on.strftime("%Y-%m-%d %H:%M:%S")).astimezone(timezone.utc)
        expires_on = parser.parse(sqlresult[4].expires_on.strftime("%Y-%m-%d %H:%M:%S")).astimezone(timezone.utc)
        isValidDate = starts_on <= now and expires_on > now
        isValid = bool(sqlresult[4].active) == True and isValidDate
        if isValid:
            discount = ProductDiscountPublic(
                discounted_amount=sqlresult[4].amount,
                discount_type=sqlresult[4].discount_type,
            )

    product_pricing = ProductPricingPublic(
        orginal_price= sqlresult[3].amount if hasattr(sqlresult[3], 'amount') else 0,
        discount=discount
    )

    product_category = None
    if hasattr(sqlresult[1], 'category_name'):
        product_category = ProductCategory(
            category_name=sqlresult[1].category_name
        )

    product_inventory = ProductInventoryPublic(
        inventory_id=sqlresult[2].quantity if hasattr(sqlresult[2], 'quantity') else None,
        quantity=sqlresult[2].quantity if hasattr(sqlresult[2], 'quantity') else 0,
        sku=sqlresult[2].sku if hasattr(sqlresult[2], 'sku') else None,
        status=sqlresult[2].status if hasattr(sqlresult[2], 'sku') else 'offline',
    )

    product = ProductPublic(
        product_id=sqlresult[0].product_id,
        product_name=sqlresult[0].product_name,
        description=sqlresult[0].description,
        slug=sqlresult[0].slug,
        pricing=product_pricing,
        category=product_category,
        inventory=product_inventory
    )

    images = session.query(ProductImage).filter(ProductImage.product_id == product_id).all()
    for image in images:
        product.product_images.append(RelatedProductImage(
            image_url=image.product_image,
            main_image=image.main_image,
        ))
    return product

@router.post("/products")
def add_product(session: SessionDep, payload: ProductRequest):
    db_table = Product(
        product_name = payload.product_name,
        description = payload.description,
        category_id = payload.category_id,
        slug = payload.product_name.lower().strip().replace(' ', '-')
    )
    session.add(db_table)
    session.commit()

@router.patch("/products/{product_id}")
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