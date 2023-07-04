from apps.auth.dependencies import get_current_active_user
from apps.users.schemas import UserRetrieve
from database import get_session
from fastapi import APIRouter, Depends, Security, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .models import *
from .schemas import *
from .services import *

router = APIRouter()


""" Catgories """


@router.get("/categories/", tags=['categories'], response_model=list[CategoryRetrieve])
async def get_categories(current_user: UserRetrieve = Security(get_current_active_user, scopes=['events']),
                         session: AsyncSession = Depends(get_session)):
    return await CategoryService(session).get_categories()


""" Tags """


@router.get("/tags/", tags=['tags'], response_model=list[TagBase])
async def get_tags(current_user: UserRetrieve = Security(get_current_active_user, scopes=['tags']),
                   session: AsyncSession = Depends(get_session)):
    return await TagService(session).get_all()


""" Events """


@router.get("/events/", tags=['events'], response_model=list[EventBase])
async def get_events(current_user: UserRetrieve = Security(
        get_current_active_user, scopes=['events']),
        session: AsyncSession = Depends(get_session)):
    return await EventService(session).get_all()


# TODO: add filter by tag
@router.get("/categories/{category_name}/", tags=['categories'], response_model=list[EventBase])
async def get_events_from_category(category_name: str,
                                   current_user: UserRetrieve = Security(
                                       get_current_active_user, scopes=['categories']),
                                   session: AsyncSession = Depends(get_session)):
    return await EventService(session).get_from_category(category_name)


@router.get("/events/{event_id}/", tags=['events'], response_model=EventRetrieve)
async def get_event(event_id: int,
                    current_user: UserRetrieve = Security(
                        get_current_active_user, scopes=['events']),
                    session: AsyncSession = Depends(get_session)):
    return await EventService(session).get(event_id)


@router.post("/events/", tags=['events'])
async def create_event(event: EventCreate,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['events']),
                       session: AsyncSession = Depends(get_session)):
    return await EventService(session).create(event, current_user.id)


@router.put("/events/{id}/", tags=['events'])
async def edit_event(id: int,
                     event: EventCreate,
                     current_user: UserRetrieve = Security(
                         get_current_active_user, scopes=['events']),
                     session: AsyncSession = Depends(get_session)):
    return await EventService(session).update(event, current_user.id)


@router.delete('/events/{id}/', tags=['events'])
async def delete_event(id: int,
                       current_user: UserRetrieve = Security(
                           get_current_active_user, scopes=['events']),
                       session: AsyncSession = Depends(get_session)):
    if await EventService(session).delete(id, current_user.id):
        return JSONResponse({"message": "Event deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)
    else:
        return JSONResponse({"message": "Something going wrong"}, status_code=status.HTTP_400_BAD_REQUEST)

""" Sign """


@router.get("/events/{event_id}/signs/", tags=['signs'], response_model=list[SignRetrieve])
async def get_signs(event_id: int,
                    current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                    session: AsyncSession = Depends(get_session)):
    return await SignService(session).get_by_event(event_id)


@router.post("/events/{event_id}/signs/", tags=['signs'], response_model=SignRetrieve)
async def create_sign(event_id: int,
                      sign: SignBase,
                      current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                      session: AsyncSession = Depends(get_session)):
    return SignService(session).create(event_id, current_user.id, sign.status)


@router.put("/signs/{id}", tags=['signs'])
async def edit_sign(id: int,
                    sign: SignBase,
                    current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                    session: AsyncSession = Depends(get_session)):
    return await SignRepository(session).update(id, sign, current_user.id)


@router.delete('/signs/{id}', tags=['signs'])
async def delete_sign(id: int,
                      current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                      session: AsyncSession = Depends(get_session)):
    if await SignService(session).delete(id, current_user.id):
        return JSONResponse({"message": "Sign deletedu successfully"}, status_code=status.HTTP_202_ACCEPTED)
    else:
        raise JSONResponse({"message": "Something going wrong"}, status_code=status.HTTP_400_BAD_REQUEST)


""" Commentaries """


@router.get('/events/{event_id}/commentaries/', tags=['commentaries'], response_model=list[CommentaryBase])
async def get_commentaries(event_id: int,
                           current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                           session: AsyncSession = Depends(get_session)):
    return await CommentaryService(session).get_from_event(event_id)


@router.post('/events/{event_id}/commentaries/', tags=['commentaries'], response_model=CommentaryBase)
async def create_commentary(event_id: int,
                            commentary: CommentaryBase,
                            current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                            session: AsyncSession = Depends(get_session)):
    return await CommentaryService(session).create(event_id, commentary.dict(), current_user.id)


@router.put('/events/{event_id}/commentaries/{commentary_id}', tags=['commentaries'], response_model=CommentaryBase)
async def edit_commentary(event_id: int,
                          commentary_id: int,
                          commentary: CommentaryBase,
                          current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                          session: AsyncSession = Depends(get_session)):
    return await CommentaryService(session).update(commentary_id, commentary, current_user.id)


@router.delete('/commentaries/{commentary_id}', tags=['commentaries'])
async def delete_commentary(commentary_id: int,
                            current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                            session: AsyncSession = Depends(get_session)):
    if await CommentaryService(session).delete(commentary_id, current_user.id):
        return JSONResponse({"message": "Commentary deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)
    else:
        raise JSONResponse({"message": "Something going wrong"}, status_code=status.HTTP_400_BAD_REQUEST)


""" Likes """


@router.get('/events/{event_id}/likes/', tags=['likes'], response_model=list[LikeBase])
async def get_likes(event_id: int,
                    current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                    session: AsyncSession = Depends(get_session)):
    return await LikeService(session).get_from_event(event_id)


@router.get('/likes/', tags=['likes'], response_model=list[LikeBase])
async def get_likes(current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                    session: AsyncSession = Depends(get_session)):
    return await LikeService(session).get_by_user_id(current_user.id)


@router.post('/events/{event_id}/like/', tags=['likes'])
async def create_likes(event_id: int,
                       current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                       session: AsyncSession = Depends(get_session)):
    return await LikeService(session).create(event_id, current_user.id)


@router.post('/likes/{id}/', tags=['likes'])
async def delete_like(id: int,
                      current_user: UserRetrieve = Security(get_current_active_user, scopes=['signs']),
                      session: AsyncSession = Depends(get_session)):
    if await LikeService(session).delete(id, current_user.id):
        return JSONResponse({"message": "Like deleted successfully"}, status_code=status.HTTP_202_ACCEPTED)
    else:
        raise JSONResponse({"message": "Something going wrong"}, status_code=status.HTTP_400_BAD_REQUEST)
    