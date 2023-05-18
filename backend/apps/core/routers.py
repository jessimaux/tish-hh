from fastapi import APIRouter, UploadFile, Security, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session

from apps.auth.dependencies import get_current_active_user
from apps.users.schemas import UserRetrieve
from .models import *
from .utils import *

router = APIRouter()


@router.post('/uploader/', tags=['core'])
async def upload_file(upload_file: UploadFile,
                      current_user: UserRetrieve = Security(get_current_active_user, scopes=['me']),
                      session: AsyncSession = Depends(get_session)):
    """File uploader
    Args:
        upload_file: file from fromdata request
    Returns:
        Return Image instance
    """
    if upload_file.content_type in ['image/jpeg', 'image/png']:
        file_url = await handle_file_upload(upload_file, f'users/{current_user.id}/images/')
        file_obj = Image(url=file_url)
        
    # TODO: file_obj = FILE ?
    elif upload_file.content_type in ['application/pdf']:
        file_url = await handle_file_upload(upload_file, f'users/{current_user.id}/docs/')
        file_obj = Image(url=file_url)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Wrong file's extension")
    session.add(file_obj)
    await session.commit()
    return file_obj
