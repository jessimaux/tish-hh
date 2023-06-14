from jose import ExpiredSignatureError, JWTError, jwt
from fastapi import Depends, HTTPException, WebSocketException, status, Security, Request, WebSocket
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from apps.users.models import User
from apps.users.schemas import UserRetrieve
from apps.users.repository import UserRepository
from .schemas import *
import settings


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        return await super().__call__(request or websocket)


oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl="/auth/token/",
                                           scopes={"profile": "Read/edit information about the current user.",
                                                   "users": "Read information about users.",
                                                   "events": "Read information about events.",
                                                   "signs": "Read information about signs.",
                                                   "tags": "Read information about tags",
                                                   "categories": "Read information about categories",
                                                   "messages": "Read and write messages",
                                                   "admin": "Admin's privilleges"})


# TODO: WebSocket handler error, need raise WebsocketException instead of HTTPException
async def get_current_user(security_scopes: SecurityScopes,
                           session: AsyncSession = Depends(get_session),
                           token: str = Depends(oauth2_scheme)) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        token_data = TokenData(**payload)
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token expired",
                            headers={"WWW-Authenticate": "Bearer"})
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    user = await UserRepository(session).get_by_username(token_data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Not enough permissions",
                                headers={"WWW-Authenticate": authenticate_value})
    return user


async def get_current_active_user(current_user: UserRetrieve = Security(get_current_user, scopes=["profile"])) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
