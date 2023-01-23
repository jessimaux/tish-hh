from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import dependencies as app_dependencies
from . import models, schemas, utils, dependencies

# TODO: add refresh token api

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token/")

@router.post("/users/register", tags=['users'], response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(app_dependencies.get_db)):
    check_email = db.query(models.User).filter(models.User.email == user.email).first()
    if check_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = utils.get_hashed_password(user.password)
    user_obj = models.User(password=hashed_password, email=user.email)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


@router.post("/users/token/", tags=['users'], response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(app_dependencies.get_db)):
    user = utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = utils.create_access_token(user.email)
    refresh_token = utils.create_refresh_token(user.email)
    return { "access_token": access_token, "refresh_token": refresh_token }


@router.get("/users/me/", tags=['users'], response_model=schemas.User)
def user(current_user: schemas.User = Depends(dependencies.get_current_active_user)):
    return current_user


@router.put('/users/me', tags=['users'], response_model=schemas.User)
def update_user(user: schemas.User, current_user: schemas.User = Depends(dependencies.get_current_active_user), db: Session = Depends(app_dependencies.get_db)):
    for key, value in user:
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user