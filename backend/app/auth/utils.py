from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status

import dependencies

from . import schemas, models
import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token/")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    check_username = get_user_by_username(db, user.username)
    if check_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    check_email = get_user_by_email(db, user.email)
    if check_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    user_obj = models.User(password=hashed_password, username=user.username, email=user.email)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(db: Session = Depends(dependencies.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user