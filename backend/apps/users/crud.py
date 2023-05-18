from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from fastapi import HTTPException
from pydantic import EmailStr

from .models import *
from .schemas import *
from database import update_foreign_key


# TODO: rewrite as general method in database.py
async def get_user_or_404(username: str, session: AsyncSession):
    user_obj = (await session.execute(select(User)
                                      .where(User.username == username))).scalar()
    if user_obj:
        return user_obj
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User doesnt exist')


# TODO: rewrite w exception, DRY
async def check_username(username: str, session: AsyncSession):
    check = (await session.execute(select(User)
                                   .where(User.username == username))).scalar()
    if check:
        return True
    else:
        return False


async def check_email(email: EmailStr, session: AsyncSession):
    check = (await session.execute(select(User)
                                   .where(User.email == email))).scalar()
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
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                        detail="Username already in use")
            # check on email exists when change email
            elif attr == 'email' and value != current_user.email:
                if not check_email(user.email):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                        detail="Email already in use")
            setattr(current_user, attr, value)

    await update_foreign_key(current_user.links, Link, user.links, session)
    await session.commit()
    return current_user
