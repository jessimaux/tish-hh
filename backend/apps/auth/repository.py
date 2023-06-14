from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *


class SessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: int, refresh_token: str) -> Session | None:
        obj = Session(user_id=user_id, refresh_token=refresh_token)
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def get_by_user_and_rt(self, user_id: int, refresh_token: str) -> Session | None:
        return (await self.session.execute(select(Session)
                                           .where(Session.user_id == user_id,
                                                  Session.refresh_token == refresh_token))).scalar()

    async def update(self, session_id: int, refresh_token: str) -> Session | None:
        obj = (await self.session.execute(update(Session)
                                          .where(Session.id == session_id)
                                          .values(refresh_token=refresh_token)
                                          .returning(Session))).scalar()
        await self.session.commit()
        return obj