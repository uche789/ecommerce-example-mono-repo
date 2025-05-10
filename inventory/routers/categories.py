from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, UploadFile, APIRouter, status
from dbsetup import DataModel
from models import (
    Category,
    CategoryUpdateRequest
)
import os
import shutil
import uuid;
from lib import is_valid_image, get_logger
import pathlib

router = APIRouter()
dm = DataModel()
SessionDep = Annotated[Session, Depends(dm.get_session)]
logger = get_logger()

@router.get('/categories')
def get_categories(session: SessionDep):
    result = session.query(Category).all()
    return result

@router.get('/categories/{category_id}')
def get_categories(session: SessionDep, category_id: int):
    result = session.get(Category, category_id)
    # TODO: Add breadcrumbs
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return result

@router.post('/categories')
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

@router.patch('/categories/{category_id}')
def update_category(session: SessionDep, payload: CategoryUpdateRequest, category_id: int):
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
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

@router.post("/categories/{category_id}/image")
def add_category_image(session: SessionDep, category_id: int, file: UploadFile) -> str:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category image not found")

    oldImageUrl = category.image_url
    new_file_name = uuid.uuid4().__str__() + pathlib.Path(file.filename).suffix
    file_location = os.path.join(os.environ.get("IMAGE_DIR"), new_file_name)

    try: 
        if not is_valid_image(file.content_type):
            logger.error("Invalid mime type")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Mime Type")
        
        with open(file_location, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
            category.image_url = file_location
            session.commit()
    except Exception as e:
        logger.error(f"Failed to upload product image: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload product image")
    
    # delete old category image
    try:
        if (oldImageUrl and os.path.exists(oldImageUrl)):
            os.remove(oldImageUrl)
    except Exception as e:
        logger.error("Failed to delete old category image", extra={
            "category_id": category_id,
            "category_image": oldImageUrl,
            "error": str(e)
        })

    return file_location