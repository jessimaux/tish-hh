from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
from apps.events.models import Event


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, password: str, email: str, username: str) -> User | None:
        obj = User(password=password, email=email, username=username)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, id: int) -> User | None:
        return (await self.session.execute(select(User)
                                           .where(User.id == id))).scalar()

    async def get_by_email(self, email: str) -> User | None:
        return (await self.session.execute(select(User)
                                           .where(User.email == email))).scalar()

    async def get_by_username(self, username: str) -> User | None:
        return (await self.session.execute(select(User)
                                           .where(User.username == username))).scalar()

    async def check_username(self, username: str) -> User | None:
        return (await self.session.execute(select(User)
                                           .where(User.username == username))).scalar()

    async def check_email(self, email: str) -> User | None:
        return (await self.session.execute(select(User)
                                           .where(User.username == email))).scalar()

    async def check_username_on_edit(self, user_id: int, username: str) -> User | None:
        return (await self.session.execute(select(User)
                                           .where(User.username == username,
                                                  User.id != user_id))).scalar()

    async def check_email_on_edit(self, user_id: int, email: str) -> User | None:
        return (await self.session.execute(select(User)
                                           .where(User.username == email,
                                                  User.id != user_id))).scalar()

    async def update(self, user_id: int, user: dict) -> User | None:
        obj = (await self.session.execute(update(User)
                                          .where(User.id == user_id)
                                          .values(**user)
                                          .returning(User))).scalar()
        await self.session.commit()
        return obj

    async def update_password(self, user_id: int, password: str) -> int:
        result = (await self.session.execute(update(User)
                                             .where(User.id == user_id)
                                             .values(password=password))).rowcount
        await self.session.commit()
        return result

    async def verify(self, user_id: int) -> int:
        result = (await self.session.execute(update(User)
                                             .where(User.id == user_id)
                                             .values(is_verifed=True))).rowcount
        await self.session.commit()
        return result


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_profile(self, user_id: int) -> User | None:
        subquery_events = (select(func.count('*').label('events_count')).select_from(Event)
                           .where(Event.created_by == user_id)
                           .subquery())
        subquery_followers = (select(func.count('*').label('followers_count')).select_from(Subscription)
                              .where(Subscription.publisher_id == user_id)
                              .subquery())
        subquery_following = (select(func.count('*').label('following_count')).select_from(Subscription)
                              .where(Subscription.subscriber_id == user_id)
                              .subquery())
        obj = (await self.session.execute(select(User, subquery_events, subquery_followers, subquery_following)
                                          .where(User.id == user_id))).first()
        return obj

    async def get_followers(self, username: str) -> list[User]:
        objs = (await self.session.execute(select(User)
                                           .join(Subscription, Subscription.publisher_id == User.id)
                                           .where(User.username == username))).scalars().all()
        return objs

    async def get_following(self, username: str) -> list[User]:
        return (await self.session.execute(select(User)
                                           .join(Subscription, Subscription.subscriber_id == User.id)
                                           .where(User.username == username))).scalars().all()


class LinkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Link | None:
        return (await self.session.execute(select(Link)
                                           .where(Link.user_id == user_id))).scalars().all()

    async def create(self, user_id: int, link: dict) -> Link | None:
        obj = Link(user_id=user_id, **link)
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def update(self, link: dict) -> Link | None:
        obj = (await self.session.execute(update(Link)
                                          .where(Link.id == link.id)
                                          .values(**link)
                                          .returning(Link))).scalar()
        await self.session.commit()
        return obj

    async def delete(self, link_id: int) -> int:
        result = (await self.session.execute(delete(Link)
                                             .where(Link.id == link_id))).rowcount
        await self.session.commit()
        return result


class SubscriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def create(self, follower_id: int, following_username: str) -> Subscription | None:
        user_subquery = (select(User.id)
                           .where(User.username == following_username)
                           .subquery())
        obj = (await self.session.execute(insert(Subscription)
                                          .values(subscriber_id=follower_id,
                                                  publisher_id=user_subquery)
                                          .returning(Subscription))).scalar()
        await self.session.commit()
        return obj

    async def get(self, follower_id: int, following_username: str) -> Subscription | None:
        user_subquery = (select(User.id)
                           .where(User.username == following_username)
                           .subquery())
        return (await self.session.execute(select(Subscription)
                                           .where(Subscription.subscriber_id == follower_id,
                                                  Subscription.publisher_id == user_subquery))).scalar()

    async def delete(self, follower_id: int, following_username: str) -> Subscription | None:
        user_subquery = (select(User.id)
                           .where(User.username == following_username)
                           .subquery())
        