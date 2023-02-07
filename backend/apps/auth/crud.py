from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import *
from .schemas import *


async def update_user(user: UserUpdate, current_user: User, session: AsyncSession):
    # for fg links
    for link in user.links:
        current_user.links.append(Link(name=link.name,
                                       link=link.link,
                                       user_id=current_user.id))

    for key, value in user:
        if key in ['links']:
            continue
        setattr(current_user, key, value)
    await session.commit()
    return current_user
