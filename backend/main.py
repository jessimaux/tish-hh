from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.auth.routers import router as auth_router
from apps.events.routers import router as events_router
import settings

app = FastAPI()
app.include_router(auth_router)
app.include_router(events_router)

app.mount("/media", StaticFiles(directory=settings.MEDIADIR), name="media")