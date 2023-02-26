from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException
from pydantic import EmailStr

from .models import *
from .schemas import *
import crud


async def get_user_or_404(session: AsyncSession, username: str | None = None, email: str | None = None):
    if username:
        user_obj = (await session.execute(select(User).where(User.username == username))).scalar()
    elif email:
        user_obj = (await session.execute(select(User).where(User.email == email))).scalar()
    if user_obj:
        return user_obj
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User doesnt exist')


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


async def check_follow(target_user: User, current_user: User, session: AsyncSession):
    check = (await session.execute(select(Subscription)
                                   .where(Subscription.subscriber_id == current_user.id,
                                          Subscription.publisher_id == target_user.id))).scalar()
    if check:
        return True
    else:
        return False


async def update_user(user: UserUpdate, current_user: User, session: AsyncSession):
    if len(user.links) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Max count of user's links is 5")
    for attr, value in user:
        if attr not in ['links']:
            # check on username exists when change username 
            if attr == 'username' and value != current_user.username:
                if not check_username(user.username):
                    raise HTTPException(
                        status_code=400, detail="Username already in use")
            # check on email exists when change email
            elif attr == 'email' and value != current_user.email:
                if not check_email(user.email):
                    raise HTTPException(
                        status_code=400, detail="Email already in use")
            setattr(current_user, attr, value)

    await crud.update_fg(current_user.links, Link, user.links, session)
    await session.commit()
    return current_user
