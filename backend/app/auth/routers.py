from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import dependencies

from . import models, schemas, utils
import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token/")

@router.post("/users/register", tags=['users'], response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    return utils.create_user(db, user)

@router.get("/users/me/", tags=['users'], response_model=schemas.User)
async def user(current_user: schemas.User = Depends(utils.get_current_active_user)):
    return current_user

@router.put('/users/me', tags=['users'], response_model=schemas.User)
async def update_user(user: schemas.User, current_user: schemas.User = Depends(utils.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    for key, value in user:
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/users/token/", tags=['users'], response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    user = utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Auth  enticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}