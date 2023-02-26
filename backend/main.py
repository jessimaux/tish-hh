from fastapi import FastAPI, UploadFile, Security, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from dependencies import get_session
from models import Image
from utils import handle_file_upload

from apps.auth.routers import router as auth_router
from apps.events.routers import router as events_router
from apps.admin.routers import router as admin_router
from apps.users.routers import router as users_router
from apps.feed.routers import router as feed_router
from apps.search.routers import router as search_router

from apps.users.schemas import UserRetrieve
from apps.auth.dependencies import get_current_active_user


app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(events_router)
app.include_router(feed_router)
app.include_router(search_router)
app.include_router(admin_router, prefix="/admin", tags=['admin'])

app.mount("/media", StaticFiles(directory=settings.MEDIADIR), name="media")


@app.post('/uploader/', tags=['core'])
async def uploader(upload_file: UploadFile,
                   current_user: UserRetrieve = Security(
                       get_current_active_user, scopes=['me']),
                   session: AsyncSession = Depends(get_session)):
    if upload_file.content_type in ['image/jpeg', 'image/png']:
        file_url = await handle_file_upload(upload_file, f'users/{current_user.id}/images/')
        file_obj = Image(url=file_url)
    elif upload_file.content_type in ['application/pdf']:
        file_url = await handle_file_upload(upload_file, f'users/{current_user.id}/docs/')
        file_obj = Image(url=file_url)
    else:
        raise HTTPException(status_code=406, detail="Wrong file's extension")
    session.add(file_obj)
    await session.commit()
    return file_obj
