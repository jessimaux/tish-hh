from pydantic import BaseModel
from apps.events.schemas import EventBase
from apps.users.schemas import UserBase, SubscriptionBase

from sqlalchemy.engine.row import Row
from typing import Any


class FeedBase(BaseModel):
    event: EventBase
    subscription: SubscriptionBase
    user: UserBase

    class Config:
        orm_mode = True