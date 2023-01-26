from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import dependencies as app_dependencies
import settings
from . import models, schemas, utils, dependencies


router = APIRouter()


@router.get("/categories/", tags=['categories'])
def get_categories(db: Session = Depends(app_dependencies.get_db)):
    categories_objs = db.query(models.Category).all()
    return categories_objs

@router.post("/categories/", tags=['categories'], response_model=schemas.CategoryBase)
def create_category(category: schemas.CategoryBase, db: Session = Depends(app_dependencies.get_db)):
    check_name = db.query(models.Category).filter(models.Category.name == category.name).first()
    if check_name:
        raise HTTPException(status_code=400, detail="Email already registered")
    category_obj = models.Category(name=category.name)
    db.add(category_obj)
    db.commit()
    return category_obj

@router.get("/categories/{name}/", tags=['categories'], response_model=schemas.CategoryBase)
def get_category(name: str, db: Session = Depends(app_dependencies.get_db)):
    category_obj = db.query(models.Category).filter(models.Category.name == name).first()
    return category_obj

@router.put("/categories/{name}/", tags=['categories'], response_model=schemas.CategoryBase)
def edit_category(name: str, category: schemas.CategoryBase, db: Session = Depends(app_dependencies.get_db)):
    category_obj = db.query(models.Category).filter(models.Category.name == name).first()
    for attr, value in category:
        setattr(category_obj, attr, value)
    db.add(category_obj)
    db.commit()
    return category_obj

@router.delete("/categories/{name}/", tags=['categories'])
def delete_category(name: str, db: Session = Depends(app_dependencies.get_db)):
    category_obj = db.query(models.Category).filter(models.Category.name == name)
    category_obj.delete()
    db.commit()
    return JSONResponse({"message": "Category deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)