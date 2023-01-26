from fastapi import FastAPI

from apps.auth.routers import router as auth_router
from apps.events.routers import router as events_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(events_router)
