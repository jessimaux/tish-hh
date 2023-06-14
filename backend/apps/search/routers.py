from fastapi import APIRouter, Depends, HTTPException, status, Security, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from apps.auth.dependencies import get_current_active_user
from apps.users.schemas import UserRetrieve
from apps.users.models import User
from apps.events.models import Event, Tag, Category
from .schemas import *
from .utils import *


router = APIRouter()

# TODO: improvements:
# - Separate element by list, e.g. tags, users and etc.
# - For every item add attribute position for order
# - HOW TO SET POSITION?


@router.get("/search/", tags=['search'])
async def search(query: str,
                 context: str = Query(default="blended", enum=['blended', 'events', 'tags', 'categories', 'users']),
                 current_user: UserRetrieve = Security(get_current_active_user, scopes=[
                                                       'events', 'tags', 'categories', 'users']),
                 session: AsyncSession = Depends(get_session)):
    return await search_func(query, context, session)
