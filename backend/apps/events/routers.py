from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import dependencies as app_dependencies
from apps.auth.dependencies import get_current_active_user
from apps.auth.schemas import UserRetrieve
from apps.auth.models import User
import settings
from . import models, schemas, utils, dependencies, crud


router = APIRouter()


""" Catgories """

@router.get("/categories/", tags=['categories'])
def get_categories(current_user: UserRetrieve = Depends(get_current_active_user),
                   db: Session = Depends(app_dependencies.get_db)):
    categories_objs = db.query(models.Category).all()
    return categories_objs

@router.post("/categories/", tags=['categories'], response_model=schemas.CategoryBase)
def create_category(category: schemas.CategoryBase, 
                    current_user: UserRetrieve = Depends(get_current_active_user),
                    db: Session = Depends(app_dependencies.get_db)):
    check_name = db.query(models.Category).filter(models.Category.name == category.name).first()
    if check_name:
        raise HTTPException(status_code=400, detail="Email already registered")
    category_obj = models.Category(name=category.name)
    db.add(category_obj)
    db.commit()
    return category_obj

@router.get("/categories/{name}/", tags=['categories'], response_model=schemas.CategoryBase)
def get_category(name: str, 
                 current_user: UserRetrieve = Depends(get_current_active_user),
                 db: Session = Depends(app_dependencies.get_db)):
    category_obj = db.query(models.Category).filter(models.Category.name == name).first()
    return category_obj

@router.put("/categories/{name}/", tags=['categories'], response_model=schemas.CategoryBase)
def edit_category(name: str, 
                  category: schemas.CategoryBase, 
                  current_user: UserRetrieve = Depends(get_current_active_user),
                  db: Session = Depends(app_dependencies.get_db)):
    category_obj = db.query(models.Category).filter(models.Category.name == name).first()
    for attr, value in category:
        setattr(category_obj, attr, value)
    db.add(category_obj)
    db.commit()
    return category_obj

@router.delete("/categories/{name}/", tags=['categories'])
def delete_category(name: str, 
                    current_user: UserRetrieve = Depends(get_current_active_user),
                    db: Session = Depends(app_dependencies.get_db)):
    category_obj = db.query(models.Category).filter(models.Category.name == name)
    category_obj.delete()
    db.commit()
    return JSONResponse({"message": "Category deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)


""" Tags """

@router.get("/tags/", tags=['tags'])
def get_tags(current_user: UserRetrieve = Depends(get_current_active_user),
             db: Session = Depends(app_dependencies.get_db)):
    tags_objs = db.query(models.Tag).all()
    return tags_objs

@router.post("/tags/", tags=['tags'], response_model=schemas.TagBase)
def create_tag(tag: schemas.TagBase, 
               current_user: UserRetrieve = Depends(get_current_active_user),
               db: Session = Depends(app_dependencies.get_db)):
    check_name = db.query(models.Tag).filter(models.Tag.name == tag.name).first()
    if check_name:
        raise HTTPException(status_code=400, detail="Email already registered")
    tag_obj = models.Tag(name=tag.name)
    db.add(tag_obj)
    db.commit()
    return tag_obj

@router.get("/tags/{name}/", tags=['tags'], response_model=schemas.TagBase)
def get_tag(name: str,
            current_user: UserRetrieve = Depends(get_current_active_user),
            db: Session = Depends(app_dependencies.get_db)):
    tag_obj = db.query(models.Tag).filter(models.Tag.name == name).first()
    return tag_obj

@router.put("/tags/{name}/", tags=['tags'], response_model=schemas.TagBase)
def edit_tag(name: str, 
             tag: schemas.TagBase, 
             current_user: UserRetrieve = Depends(get_current_active_user),
             db: Session = Depends(app_dependencies.get_db)):
    tag_obj = db.query(models.Tag).filter(models.Tag.name == name).first()
    for attr, value in tag:
        setattr(tag_obj, attr, value)
    db.add(tag_obj)
    db.commit()
    return tag_obj

@router.delete("/tags/{name}/", tags=['tags'])
def delete_tag(name: str, 
               current_user: UserRetrieve = Depends(get_current_active_user),
               db: Session = Depends(app_dependencies.get_db)):
    tag_obj = db.query(models.Tag).filter(models.Tag.name == name)
    tag_obj.delete()
    db.commit()
    return JSONResponse({"message": "Tag deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)


""" Events """

@router.get("/events/", tags=['events'])
def get_events(current_user: UserRetrieve = Depends(get_current_active_user),
               db: Session = Depends(app_dependencies.get_db)):
    events_objs = db.query(models.Event).all()
    return events_objs

@router.get("/events/{id}", tags=['events'], response_model=schemas.EventRetrieve)
def get_event(id: int,
              current_user: UserRetrieve = Depends(get_current_active_user),
              db: Session = Depends(app_dependencies.get_db)):
    event_obj = db.query(models.Event).filter(models.Event.id == id).first()
    return event_obj

@router.post("/events/", tags=['events'], response_model=schemas.EventRetrieve)
def create_event(event: schemas.EventCreate, 
                 current_user: UserRetrieve = Depends(get_current_active_user),
                 db: Session = Depends(app_dependencies.get_db)):        
    event_obj = crud.create_event(event, db)
    return event_obj

@router.put("/events/{id}", tags=['events'], response_model=schemas.EventRetrieve)
def edit_event(id: int,
               event: schemas.EventCreate,
               current_user: UserRetrieve = Depends(get_current_active_user),
               db: Session = Depends(app_dependencies.get_db)):
    event_obj = crud.edit_event(id, event, db)
    return event_obj

@router.delete('/events/{id}', tags=['events'])
def delete_event(id: int,
                 current_user: UserRetrieve = Depends(get_current_active_user),
                 db: Session = Depends(app_dependencies.get_db)):
    event_obj = db.query(models.Event).filter(models.Event.id == id)
    event_obj.delete()
    db.commit()
    return JSONResponse({"message": "Event deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)


""" Sign """

@router.get("/signs/", tags=['signs'])
def get_signs(current_user: UserRetrieve = Depends(get_current_active_user),
              db: Session = Depends(app_dependencies.get_db)):
    sign_objs = db.query(models.Sign).all()
    return sign_objs

@router.post("/signs/", tags=['signs'], response_model=schemas.SignRetrieve)
def create_sign(sign: schemas.SignBase, 
                 current_user: UserRetrieve = Depends(get_current_active_user),
                 db: Session = Depends(app_dependencies.get_db)):        
    sign_obj = models.Sign(user_id=sign.user_id, event_id=sign.event_id, status=sign.status)
    db.add(sign_obj)
    db.commit()
    db.refresh(sign_obj)
    return sign_obj

@router.put("/signs/{id}", tags=['signs'], response_model=schemas.SignRetrieve)
def edit_sign(id: int,
               sign: schemas.SignBase,
               current_user: UserRetrieve = Depends(get_current_active_user),
               db: Session = Depends(app_dependencies.get_db)):
    sign_obj = db.query(models.Sign).filter(models.Sign.id == id).first()
    for attr, value in sign:
        setattr(sign_obj, attr, value)
    db.add(sign_obj)
    db.commit()
    return sign_obj

@router.delete('/signs/{id}', tags=['signs'])
def delete_sign(id: int,
                 current_user: UserRetrieve = Depends(get_current_active_user),
                 db: Session = Depends(app_dependencies.get_db)):
    sign_obj = db.query(models.Sign).filter(models.Sign.id == id)
    sign_obj.delete()
    db.commit()
    return JSONResponse({"message": "Sign deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)
