from fastapi import APIRouter, Security, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, text

from database import get_session
from apps.auth.dependencies import get_current_active_user
from apps.users.schemas import UserRetrieve
from apps.users.models import Subscription, User
from apps.events.models import Sign, Event
from .schemas import *


router = APIRouter()


@router.get('/feed/', tags=['feed'])
async def get_feed(current_user: UserRetrieve = Security(get_current_active_user, scopes=['me']),
                   session: AsyncSession = Depends(get_session)):
    statement = (select(Event, Subscription, User)
                 .where(Subscription.subscriber_id == current_user.id)
                 .join(Sign, Subscription.publisher_id == Sign.user_id)
                 .join(Event, Sign.event_id == Event.id)
                 .join(User, Subscription.publisher_id == User.id))
    result = (await session.execute(statement)).all()
    return [FeedBase(event=item[0], subscription=item[1], user=item[2]) for item in result]
