from fastapi import APIRouter, UploadFile, Security, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session

from apps.auth.dependencies import get_current_active_user
from apps.users.schemas import UserRetrieve
from .models import *
from .services import *

uploader_router = APIRouter()


@uploader_router.post('/uploader/', tags=['uploader'], response_model=ImageBase)
async def upload_file(upload_file: UploadFile,
                      current_user: UserRetrieve = Security(get_current_active_user, scopes=['profile']),
                      session: AsyncSession = Depends(get_session)):
    return await UploaderService(session).upload(upload_file)
