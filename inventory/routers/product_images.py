import os
import pathlib
from typing import Annotated
import uuid
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter, Response, UploadFile
from models import (
    Product, ProductImage
)
from sqlalchemy import update
from lib import DataModel, is_valid_image, get_logger


router = APIRouter()
dm = DataModel()
SessionDep = Annotated[Session, Depends(dm.get_session)]
logger = get_logger()


@router.get("/products/{product_id}/images")
def set_product_main_image(session: SessionDep, product_id: int):
    result = session.query(ProductImage).filter(ProductImage.product_id == product_id).all()
    return result

@router.post("/products/{product_id}/images/{product_image_id}/main")
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

@router.post("/products/{product_id}/images")
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
            file_location = os.path.join(os.environ.get("IMAGE_DIR"), new_file_name)
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
            logger.error(f"Failed to upload product image {e}")
            files_result["skipped"].append(file.filename)
    
    return files_result

@router.delete('/products/{product_id}/images/{product_image_id}')
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
        logger.error(f"Failed to delete product image {e}")
        raise HTTPException(status_code=500, detail='Failed to delete product image')

    return Response(status_code=204)