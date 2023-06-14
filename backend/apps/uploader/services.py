import os
import uuid

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles

import settings
from .repository import *
from .schemas import ImageBase


class UploaderService:
    def __init__(self, session: AsyncSession) -> None:
        self.image_repository = ImageRepository(session)

    async def _handle_file_upload(self, file: UploadFile) -> tuple[str, str]:
        _, extension = os.path.splitext(file.filename)
        content = await file.read()
        file_name = f'{uuid.uuid4().hex}{extension}'
        file_path = os.path.join(settings.MEDIADIR, file_name)
        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(content)
        return file_name

    async def upload(self, upload_file: UploadFile, user_id: int) -> ImageBase | None:
        if upload_file.content_type in ['image/jpeg', 'image/png']:
            file_name = await self._handle_file_upload(upload_file)
            img_obj = await self.image_repository.create(file_name, user_id)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Wrong image extension")
        return ImageBase.from_orm(img_obj)

    async def delete(self, image_id: int, user_id: int) -> None:
        image_obj = await self.image_repository.delete(image_id, user_id)
        file_path = f'{settings.MEDIADIR}{image_obj.filename}'
        if os.path.exists(file_path):
            os.remove(file_path)
