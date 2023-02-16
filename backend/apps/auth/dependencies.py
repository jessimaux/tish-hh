import datetime
from functools import wraps

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy import select
from sqlalchemy.orm import selectinload, lazyload
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session
from .schemas import *
from .models import *
import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token/",
                                     scopes={"me": "Read information about the current user.",
                                             "users": "Read information about users.", 
                                             "events": "Read information about events.",
                                             "signs": "Read information about signs.",
                                             "tags": "Read information about tags",
                                             "categories": "Read information about categories",
                                             "admin": "Admin's privilleges"},)

async def get_current_user(security_scopes: SecurityScopes,
                           session: AsyncSession = Depends(get_session), 
                           token: str = Depends(oauth2_scheme)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        token_data = TokenData(**payload)
        if datetime.datetime.fromtimestamp(token_data.exp) < datetime.datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_res = await session.execute(select(User)
                                     .where(User.email == token_data.email))
    user = user_res.scalar()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(current_user: UserRetrieve = Security(get_current_user, scopes=["me"])):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
