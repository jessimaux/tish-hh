from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.users.models import User
from apps.events.models import Event, Tag, Category


async def search_func(query: str, context: str, session: AsyncSession):
    if context == 'blended':
        results = list()
        for item in ['events', 'tags', 'categories', 'users']:
            results.extend(await search_func(query, item, session))
        return results
    if context == 'events':
        statement_events = (select(Event).where(Event.name.ilike(query)))
        events = (await session.execute(statement_events)).scalars().all()
        events_w_type = [{'type': 'event', 'item': event} for event in events]
        return events_w_type
    if context == 'tags':
        statement_tags = (select(Tag).where(Tag.name.ilike(query)))
        tags = (await session.execute(statement_tags)).scalars().all()
        tags_w_type = [{'type': 'tag', 'item': tag} for tag in tags]
        return tags_w_type
    if context == 'categories':
        statement_categories = (
            select(Category).where(Category.name.ilike(query)))
        categories = (await session.execute(statement_categories)).scalars().all()
        categories_w_type = [{'type': 'category', 'item': category}
                             for category in categories]
        return categories_w_type
    if context == 'users':
        statement_users = (select(User).where(User.name.ilike(query)))
        users = (await session.execute(statement_users)).scalars().all()
        users_w_type = [{'type': 'user', 'item': user} for user in users]
        return users_w_type