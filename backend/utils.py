import os
from fastapi import HTTPException, UploadFile
import aiofiles
import uuid

import settings

async def handle_file_upload(file: UploadFile, upload_path: str, file_types: list[str]):
    _, ext = os.path.splitext(file.filename)
    file_dir = os.path.join(settings.MEDIADIR, upload_path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    
    content = await file.read()
    if file.content_type not in file_types:
        raise HTTPException(status_code=406, detail="Only .jpeg or .png  files allowed")
    file_name = f'{uuid.uuid4().hex}{ext}'
    file_path = os.path.join(file_dir, file_name)
    file_url = settings.MEDIAURL + upload_path + file_name
    async with aiofiles.open(file_path, mode='wb') as f:
        await f.write(content)

    return file_url