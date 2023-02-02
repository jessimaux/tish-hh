import datetime
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

import dependencies as app_dependencies
import settings
from . import models, schemas, utils, dependencies
from email_client import send_verification_code

# TODO: 
# Complete jwt auth: at in coockie, rt localstorage
# Permission for register, refresh
# Change password, password email reset

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token/")

@router.post("/users/reg/", tags=['users'], response_model=schemas.UserRetrieve)
async def create_user(user: schemas.UserCreate, request: Request, db: Session = Depends(app_dependencies.get_db)):
    check_email = db.query(models.User).filter(models.User.email == user.email).first()
    if check_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    check_username = db.query(models.User).filter(models.User.username == user.username).first()
    if check_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = utils.get_hashed_password(user.password)
    user_obj = models.User(password=hashed_password, email=user.email, username=user.username)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    await send_verification_code(user_obj, request, db)
    return user_obj


@router.post("/users/token/", tags=['users'], response_model=schemas.Token)
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(app_dependencies.get_db)):
    user = utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = utils.create_access_token(user.email)
    refresh_token = utils.create_refresh_token(user.email)
    
    response.set_cookie('access_token', access_token,  settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return { "access_token": access_token, "refresh_token": refresh_token }


@router.get('/users/refresh/', tags=['users'])
def refresh_token(token: str, request: Request, response: Response, db: Session = Depends(app_dependencies.get_db)):
    try:
        payload = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, settings.JWT_ALGORITHM)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token"
        )
    user_obj = db.query(models.User).filter(models.User.email == payload['email']).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect username or password")
    access_token = utils.create_access_token(user_obj.email)
    return {'access_token': access_token}


@router.get("/users/me/", tags=['users'], response_model=schemas.UserRetrieve)
def get_user(current_user: schemas.UserRetrieve= Depends(dependencies.get_current_active_user)):
    return current_user


@router.put('/users/me/', tags=['users'], response_model=schemas.UserRetrieve)
def update_user(user: schemas.UserRetrieve, current_user: schemas.UserRetrieve = Depends(dependencies.get_current_active_user), db: Session = Depends(app_dependencies.get_db)):
    for key, value in user:
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get('/users/verifyemail/{token}/', tags=['users'])
def verify_me(token: str, db: Session = Depends(app_dependencies.get_db)):
    try:
        jwt_decoded = jwt.decode(token, settings.JWT_VERIFICATION_SECRET_KEY, settings.JWT_ALGORITHM)
        if datetime.datetime.fromtimestamp(jwt_decoded['exp']) < datetime.datetime.now():
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="Token expired"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate token"
        )
    user_obj = db.query(models.User).filter(models.User.email == jwt_decoded['email']).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid code or user doesn't exist")
    if user_obj.is_verifed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Email can only be verified once')
    user_obj.is_verifed = True
    db.commit()
    return {
        "status": "success",
        "message": "Account verified successfully"
    }
