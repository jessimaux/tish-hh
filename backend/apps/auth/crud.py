from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException
from pydantic import EmailStr

from .models import *
from .schemas import *
import crud


async def check_username(username: str, session: AsyncSession):
    check = (await session.execute(select(User).where(User.username == username))).scalar()
    if check:
        return True
    else:
        return False
    
async def check_email(email: EmailStr, session: AsyncSession):
    check = (await session.execute(select(User).where(User.email == email))).scalar()
    if check:
        return True
    else:
        return False


async def update_user(user: UserUpdate, current_user: User, session: AsyncSession):
    for attr, value in user:
        if attr not in ['links']:
            if attr == 'username' and value != current_user.username:
                if not check_username(user.username):
                    raise HTTPException(
                        status_code=400, detail="Username already in use")
            elif attr == 'email' and value != current_user.email:
                if not check_email(user.email):
                    raise HTTPException(
                        status_code=400, detail="Email already in use")
            setattr(current_user, attr, value)

    await crud.update_fg(current_user.links, Link, user.links, session)
    await session.commit()
    return current_user
